#!/bin/bash
# PASS acceptance for alibaba/anolisa#2543 sub-B (PKG-010): %preun fail-closed.
# Extracts the %preun scriptlet from cosh-ng.spec.in, expands macros the way
# rpmbuild does, and drives it with a real user (useradd -s /usr/bin/cosh)
# inside an alinux3 container using real getent/awk.
set -u
SPEC=/work/src/cosh-ng/cosh-ng.spec.in
OUT=/out

predicate=$(sed -n 's/^%define cosh_replacement_ready //p' "$SPEC")
predicate=${predicate//'%{_bindir}'//usr/bin}
predicate=${predicate//'%%'/%}
preun_raw=$(awk '/^%preun$/{f=1;next} /^%post/{f=0} f' "$SPEC")
preun=${preun_raw//'%{cosh_replacement_ready}'/$predicate}
preun=${preun//'%{_bindir}'//usr/bin}
printf '%s\n' "$preun" > "$OUT/preun-scriptlet.sh"
echo "== extracted %preun (expanded) =="
printf '%s\n' "$preun"

fail=0
run_preun() { bash -c "$preun" cosh-preun "$1"; }

echo "== case 1: erase with cosh login-shell user =="
useradd -m -s /usr/bin/cosh coshuser
run_preun 0 2> /tmp/case1.err; rc=$?
cat /tmp/case1.err
echo "rc=$rc (expect 1)"
[ "$rc" -eq 1 ] || fail=1
grep -q 'coshuser' /tmp/case1.err || fail=1

echo '== case 2: upgrade ($1>=1) with same user =='
run_preun 1; rc=$?
echo "rc=$rc (expect 0)"
[ "$rc" -eq 0 ] || fail=1

echo "== case 3: erase without cosh users =="
userdel -r coshuser
run_preun 0; rc=$?
echo "rc=$rc (expect 0)"
[ "$rc" -eq 0 ] || fail=1

if [ "$fail" -eq 0 ]; then
  echo "VERDICT: PASS (preun blocks erase with cosh users, allows upgrade and clean erase)"
  exit 0
fi
echo "VERDICT: FAIL"
exit 1
