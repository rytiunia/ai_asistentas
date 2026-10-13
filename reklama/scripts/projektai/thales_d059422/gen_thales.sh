set -e
O=/home/claude/thales/out4; rm -rf $O; mkdir -p $O
cd /home/claude/ai_asistentas/reklama/scripts/projektai/thales_d059422
THALES_ORDER=${THALES_ORDER:-ALT0000_00.00_RS} THALES_SRC=/root/.claude/uploads/c23df06d-56e2-5672-9d6a-d294e74934f5/cd85da0a-APS_Communication_-_Thales_Campus_v5_phase_2.pdf THALES_OUT=$O python3 thales_pylons.py all 2>&1 | tail -2
cd $O && python3 - <<'PY'
import sys, json, os, subprocess, pymupdf
sys.path.insert(0,'/home/claude/ai_asistentas/reklama/scripts')
import lapas_core as K
d=pymupdf.open(); art=[]
for f in ['ENT_1_GA.pdf','ENT_2_SEC.pdf','BLD_1_GA.pdf','BLD_2_SEC.pdf','PMMA_5.pdf']:
    off=len(d); d.insert_pdf(pymupdf.open(f))
    if os.path.exists(f+'.art.json'): art += [a[:4]+[a[4]+off] for a in json.load(open(f+'.art.json'))['art']]
fn='Drawing_Thales_Campus_Velizy_D059422_revC.pdf'
d.save('tmp_merge.pdf', garbage=3, deflate=True); K.pdf_fix_fonts('tmp_merge.pdf')
subprocess.run(['qpdf','--object-streams=disable','tmp_merge.pdf',fn],check=True); os.remove('tmp_merge.pdf')   # v171 CorelDRAW
json.dump({'art':art}, open(fn+'.art.json','w'))
PY
pdftoppm -r 110 -png Drawing_Thales_Campus_Velizy_D059422_revC.pdf c
