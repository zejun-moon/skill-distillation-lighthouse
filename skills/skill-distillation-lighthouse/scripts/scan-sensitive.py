#!/usr/bin/env python3
"""scan-sensitive.py —— 通用脱敏扫描器（可拷到任何仓库直接用）

扫什么（按后果从重到轻）：
  - 凭据：私钥块 / AWS AKIA / GitHub token / GitLab token / Slack token /
          明文 password|secret|token|api_key 赋值 / Bearer token
  - 内网地址：真实 IPv4（校验八位组）/ 内网域名（*.test.local 等）/ 私有仓库地址
  - 内部标识：uuid（仪表盘、文件夹 uid 一律应参数化）/ 内部账号前缀 / 真实姓名
  - 邮箱（占位邮箱放行）

豁免：行内写 `# scan: allow`（兼容 `# check_repo: allow`）即可豁免该行，**必须写明理由**。

用法：
    python3 scan-sensitive.py                      # 扫当前仓库
    python3 scan-sensitive.py --root /path/to/repo # 扫别的仓库
    python3 scan-sensitive.py --rules my.json      # 追加/覆盖规则
    python3 scan-sensitive.py --json report.json   # 输出 JSON 报告
    python3 scan-sensitive.py --exclude 'docs/*'   # 排除路径（glob）
    python3 scan-sensitive.py path/to/file ...     # 只扫指定路径

退出码 = 命中数（0 = 干净；>0 = 有命中）。
Python 3.6+，只用标准库。
"""
import argparse
import fnmatch
import json
import os
import re
import sys

ALLOW_MARKERS = ("scan: allow", "check_repo: allow")

# ── 默认规则 ────────────────────────────────────────────────────────────────
DEFAULT_RULES = {
    # 允许出现的 IP（协议常量，不是真实主机）
    "ip_allow": ["0.0.0.0", "127.0.0.1", "255.255.255.255", "::1"],
    # 占位邮箱
    "email_allow": [
        "user@example.com", "you@example.com", "admin@example.com",
        "noreply@example.com", "test@example.com",
    ],
    # 内网 / 真实主机名特征
    "host_patterns": [
        [r"\b[\w.-]+\.test\.local\b", "内网测试域名（*.test.local）"],
        [r"\b[\w.-]+\.test\.com\b", "内网测试域名（*.test.com）"],
        [r"\b[\w.-]+\.internal\b", "内部域名（*.internal）"],
        [r"\bdocker\.m\.daocloud\.io\b", "内部镜像加速源"],
        [r"\bharbor\.[\w.-]+\b", "私有镜像仓库地址"],
        [r"\bgitlab\.[\w.-]+\b", "私有 GitLab 地址"],
    ],
    # 个人 / 组织标识（按自己的环境改；仓库自己的公开账号不要列进来）
    # ⚠️ 规则定义行必须自带豁免标记 —— 否则扫描器会把自己扫出来（自指误报）
    "identity_patterns": [
        [r"\bzhongzj\b", "个人标识 zhongzj"],  # scan: allow —— 这是规则本身
        [r"\bzzj-[a-z]", "内部命名空间前缀 zzj-"],  # scan: allow —— 这是规则本身
        [r"\bseaworld008\b", "第三方账号标识"],  # scan: allow —— 这是规则本身
        [r"钟泽军", "真实姓名"],  # scan: allow —— 这是规则本身
    ],
    # 凭据特征
    "credential_patterns": [
        [r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私钥文件内容"],
        [r"\bAKIA[0-9A-Z]{16}\b", "AWS AccessKey"],
        [r"\bghp_[A-Za-z0-9]{20,}", "GitHub token (ghp_)"],
        [r"\bgithub_pat_[A-Za-z0-9_]{20,}", "GitHub token (github_pat_)"],
        [r"\bgho_[A-Za-z0-9]{20,}", "GitHub token (gho_)"],
        [r"\bglpat-[A-Za-z0-9_-]{16,}", "GitLab token"],
        [r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"],
        [r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key)"
         r"\s*[:=]\s*[\"'][^\"'\s$<>{}]{6,}[\"']", "疑似明文口令/密钥赋值"],
        [r"(?i)\bAuthorization:\s*Bearer\s+[A-Za-z0-9._\-]{16,}", "Bearer token"],
    ],
    # 内部资源 uid（仪表盘/文件夹 uid 一律应参数化）
    "uuid_pattern": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
}

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b(?![0-9])")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

# RFC 2606 / 6761 保留域名 —— 占位符，不是真实主机，必须放行
RESERVED_EXAMPLE_DOMAINS = ("example.com", "example.org", "example.net")


def is_reserved_example(host):
    """host 是否是保留的示例域名（example.com/.org/.net）及其子域。"""
    host = (host or "").lower().rstrip(".")
    for d in RESERVED_EXAMPLE_DOMAINS:
        if host == d or host.endswith("." + d):
            return True
    return False

TEXT_EXT = {
    ".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sh", ".bash", ".cfg",
    ".ini", ".toml", ".env", ".example", ".xml", ".html", ".js", ".ts", "",
}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
             "_private", ".mypy_cache", ".pytest_cache", "dist", "build"}


def is_real_ipv4(text):
    """八位组全部 <= 255 才算合法 IPv4（否则只是数字串，如版本号 999.999.999.999）。"""
    for part in text.split("."):
        if len(part) > 1 and part[0] == "0":
            return False
        if int(part) > 255:
            return False
    return True


def compile_rules(rules):
    """把规则字典编译成正则。"""
    out = {
        "ip_allow": set(rules.get("ip_allow", [])),
        "email_allow": {e.lower() for e in rules.get("email_allow", [])},
        "host": [(re.compile(p), w) for p, w in rules.get("host_patterns", [])],
        "identity": [(re.compile(p), w) for p, w in rules.get("identity_patterns", [])],
        "credential": [(re.compile(p), w) for p, w in rules.get("credential_patterns", [])],
        "uuid": re.compile(rules.get("uuid_pattern", DEFAULT_RULES["uuid_pattern"])),
    }
    return out


def scan_line(path, lineno, line, rules):
    """返回该行命中的问题列表。"""
    if any(m in line for m in ALLOW_MARKERS):
        return []

    hits = []

    for m in IPV4_RE.finditer(line):
        ip = m.group(0)
        if ip in rules["ip_allow"]:
            continue
        # 形如 10.0.0.x 的占位写法不算真实 IP
        if re.search(r"\.x\b", line[max(0, m.start() - 4):m.end() + 2]):
            continue
        if not is_real_ipv4(ip):
            continue
        hits.append("真实 IPv4 地址: %s" % ip)

    for rx, why in rules["host"]:
        for m in rx.finditer(line):
            if is_reserved_example(m.group(0)):
                continue
            hits.append("%s: %s" % (why, m.group(0)))

    for rx, why in rules["identity"]:
        for m in rx.finditer(line):
            hits.append("%s: %s" % (why, m.group(0)))

    for rx, why in rules["credential"]:
        if rx.search(line):
            hits.append(why)

    for m in rules["uuid"].finditer(line):
        hits.append("内部资源 uid（uuid）: %s" % m.group(0))

    for m in EMAIL_RE.finditer(line):
        email = m.group(0).lower()
        if email in rules["email_allow"]:
            continue
        # 保留示例域名（user@example.com 之类）不是真实邮箱
        if is_reserved_example(email.split("@", 1)[1]):
            continue
        hits.append("邮箱地址: %s" % m.group(0))

    return ["%s:%d  %s" % (path, lineno, h) for h in hits]


def iter_files(root, targets, excludes):
    """产出待扫描的文件路径。"""
    if targets:
        base = root
        for t in targets:
            p = t if os.path.isabs(t) else os.path.join(root, t)
            if os.path.isfile(p):
                yield p
            elif os.path.isdir(p):
                for dirpath, dirnames, filenames in os.walk(p):
                    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                    for f in filenames:
                        yield os.path.join(dirpath, f)
        return

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root).replace("\\", "/")
            if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
                continue
            yield full


def is_text_file(path):
    if os.path.splitext(path)[1].lower() in TEXT_EXT:
        return True
    try:
        with open(path, encoding="utf-8") as f:
            f.read(4096)
        return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(
        description="通用脱敏扫描器（扫描真实 IP / 内网域名 / 凭据 / 内部标识 / 邮箱）")
    ap.add_argument("--root", default=".", help="扫描根目录（默认当前目录）")
    ap.add_argument("--rules", default="", help="规则 JSON 文件（覆盖默认规则）")
    ap.add_argument("--json", default="", help="把结果写成 JSON 到该路径")
    ap.add_argument("--exclude", action="append", default=[],
                    help="排除的路径 glob（可多次）")
    ap.add_argument("--quiet", action="store_true", help="只输出命中数")
    ap.add_argument("paths", nargs="*", help="只扫这些路径（相对 --root 或绝对）")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    rules_conf = dict(DEFAULT_RULES)
    if args.rules:
        with open(args.rules, encoding="utf-8") as f:
            user = json.load(f)
        for k, v in user.items():
            rules_conf[k] = v
    rules = compile_rules(rules_conf)

    findings = []
    scanned = 0
    for path in iter_files(root, args.paths, args.exclude):
        if not os.path.isfile(path):
            continue
        if not is_text_file(path):
            continue
        rel = os.path.relpath(path, root).replace("\\", "/")
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.read().split("\n")
        except Exception:
            continue
        scanned += 1
        for lineno, line in enumerate(lines, 1):
            for h in scan_line(rel, lineno, line, rules):
                findings.append(h)

    if not args.quiet:
        for h in findings:
            print(h)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({
                "root": root,
                "scanned_files": scanned,
                "hits": findings,
                "hit_count": len(findings),
            }, f, ensure_ascii=False, indent=2)

    print("扫描 %d 个文件，命中 %d 处" % (scanned, len(findings)))
    if findings:
        print("豁免方式：在该行加 `# scan: allow` 并写清理由。")
    return len(findings)


if __name__ == "__main__":
    sys.exit(main())
