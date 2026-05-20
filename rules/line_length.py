NAME = "line-length"
DEFAULT_ENABLED = True


def check_line_length(lines, config):
    # Hard disable (guaranteed override)
    rule = config.get(NAME)

    if rule is False:
        return []

    if isinstance(rule, dict):
        max_len = rule.get("max", 120)
    else:
        max_len = 120

    issues = []

    for i, line in enumerate(lines, start=1):
        width = len(line.rstrip("\n"))

        if max_len is not None and width > max_len:
            issues.append((i, f"line exceeds {max_len} columns ({width}) [{NAME}]"))

    return issues


def check(file, line, lineno, ctx, config):
    rule = config.get(NAME)

    if rule is False:
        return []

    if isinstance(rule, dict):
        max_len = rule.get("max", 120)
    else:
        max_len = 120

    width = len(line.rstrip("\n"))
    if max_len is not None and width > max_len:
        from markdown_lint import LintIssue

        return [
            LintIssue(file, lineno, NAME, f"line exceeds {max_len} columns ({width})")
        ]
    return []
