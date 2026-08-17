#!/bin/bash
# FAIL baseline repro for alibaba/anolisa#2543 sub-A (PKG-007.shells-no-newline)
# Runs the UNMODIFIED %post lua scriptlet (extracted from cosh-ng.spec.in)
# via the real rpm embedded lua interpreter inside an alinux3 container,
# against an /etc/shells fixture that lacks a trailing newline.
set -u
SPEC=/work/src/cosh-ng/cosh-ng.spec.in
OUT=/out

# 1. Extract %post lua scriptlet from spec; expand %{_bindir} the same way
#    rpmbuild does when writing the scriptlet into the package header
post=$(awk '/^%post -p <lua>$/{f=1;next} /^%/{f=0} f' "$SPEC" | sed 's|%{_bindir}|/usr/bin|g')
printf '%s\n' "$post" > "$OUT/post-scriptlet.lua"
echo "== extracted %post lua =="
printf '%s\n' "$post"

# 2. Fixture: /etc/shells without trailing newline (issue variant)
printf '/bin/sh\n/bin/bash' > /etc/shells
echo "== fixture (cat -A) =="
cat -A /etc/shells

# 3. First run (install path)
rpm --eval "%{lua:${post}}"
echo "rc_first=$?"
echo "== after first run (cat -A) =="
cat -A /etc/shells

# 4. Second run (reinstall/upgrade path) to expose non-idempotent growth
rpm --eval "%{lua:${post}}"
echo "rc_second=$?"
echo "== after second run (cat -A) =="
cat -A /etc/shells

# 5. Verdict: contract is "single entry, correctly newline-terminated, idempotent"
glued=$(grep -c '^/bin/bash/usr/bin/cosh$' /etc/shells)
entries=$(grep -c '^/usr/bin/cosh$' /etc/shells)
echo "glued_lines=$glued standalone_entries=$entries"
if [ "$glued" -eq 0 ] && [ "$entries" -eq 1 ]; then
  echo "VERDICT: PASS (single clean entry, idempotent)"
  exit 0
fi
echo "VERDICT: FAIL (PKG-007 reproduced: glued=$glued entries=$entries)"
exit 1
