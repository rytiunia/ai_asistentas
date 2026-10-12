# POWER Brotorvet / posisjon 3a (Imagon, 2026-10-11) - reklama v97
2 vnt. 3171 x 330, P6_8mm+foil ORACAL 8500-034, šonai RAL 9005, gylis 60, rėmas U 30x30x2 + ausėlės RAL 7024,
220V 1,5 m laidas (be TRAFO BOX), fasadas = betonas (klientas galinę plokštę vadina fasadu - montuojama ant fasado).
Kliento failas - senas BrandFactory brėžinys (keli vaizdai viename lape): naudojamas viršutinis priekio vaizdas.
```
RAILS_JSON=rails.json python3 ../../braizyti_begeliai.py spec.json POWER_Brotorvet_3a.pdf
python3 ../../p6_dxf.py Drawing_Power_Brotorvet.pdf dxf --scale 12.502 --names POWER --prefix POWER_3a --rail 30 \
   --cable top --no-letters --rails-json rails.json --crop 95,110,835,210 --fill 0.92,0.41,0.06
```
Laukiama (v99): bėgeliai 2970 / 3020 (apvalinta 5 mm), statmenys 245 (6 m taisyklė visam užsakymui, 2 vnt.), 3 strypai [3020+2970] x 2 + statmenys;
8 ausėlės (poros), 3 statmenys; DXF 31 skylė, drenažas Ø8: P 1, O 1, W 1, E 1, R 2.
