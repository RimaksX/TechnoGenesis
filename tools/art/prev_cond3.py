"""Точный предпросмотр всех кабелей и труб: прямой участок и поворот с тремя ветвями."""
import sys, json; sys.path.insert(0,'.')
import prev_cond2 as Q
from kontur_gen import preview3d as P
from PIL import Image
import numpy as np
A=Q.A
def build(id_, jobs):
    core=json.load(open(A/f"models/block/{id_}_core.json"))
    tex=core["textures"]["t"]
    img=Image.open(A/"textures"/(tex.split(":")[1]+".png")).convert("RGBA")
    kx,ky=img.width/16,img.height/16
    model=Q.FM(); place={}; allj=[]
    for name,(rx,ry) in jobs:
        m=json.load(open(A/f"models/block/{id_}_{name}.json"))
        for e in m["elements"]: allj.append((e,(rx,ry)))
    for bi,(e,(rx,ry)) in enumerate(allj):
        R=Q.mat(rx,ry); a0,b0=np.array(e["from"],float),np.array(e["to"],float); c=np.array([8.,8.,8.])
        pa,pb=R@(a0-c)+c,R@(b0-c)+c; a,b=np.minimum(pa,pb),np.maximum(pa,pb)
        box=Q.FB(); box.a,box.b,box.rot=list(a),list(b),None; box.frames,box.frot,box.faces={},{},[]
        for fn,f in e["faces"].items():
            O,U,V=Q.frame(fn,a0,b0); O2=R@(O-c)+c; U2=R@np.array(U); V2=R@np.array(V); g=Q.rot_name(fn,R); box.faces.append(g)
            ext=b-a; box.frames[g]=(O2,U2,V2,abs(U2@ext),abs(V2@ext)); box.frot[g]=f.get("rotation",0)
            u0,v0,u1,v1=f["uv"]
            place[(bi,g)]=(int(round(min(u0,u1)*kx)),int(round(min(v0,v1)*ky)),max(1,int(round(abs(u1-u0)*kx))),max(1,int(round(abs(v1-v0)*ky))))
        model.boxes.append(box)
    return model,img,place
D={"north":(0,0),"east":(0,90),"south":(0,180),"west":(0,270),"up":(270,0),"down":(90,0)}
def tile(id_, cable):
    if cable:
        straight=[("side",D["east"]),("side",D["west"]),("mid",(0,90))]
    else:
        straight=[("core",(0,0)),("side",D["east"]),("side",D["west"])]
    bend=[("core",(0,0)),("side",D["east"]),("side",D["north"]),("side",D["up"])]
    out=[]
    for jobs in (straight,bend):
        m,at,pl=build(id_,jobs); out.append(P.render(m,at,pl,yaw=35,pitch=28,px=16,bg=(190,194,200),extent=11))
    return out
if __name__=="__main__":
    ids=[("copper_wire",1),("ceramic_cable",1),("armored_cable",1),("superconducting_cable",1),
         ("item_pipe",0),("item_pipe_fast",0),("item_pipe_express",0),("item_pipe_ultra",0),
         ("fluid_pipe",0),("fluid_pipe_fast",0),("fluid_pipe_heavy",0),("fluid_pipe_ultra",0)]
    tiles=[]
    for id_,c in ids: tiles+=tile(id_,c)
    w,h=tiles[0].size; cols=4
    rows=(len(tiles)+cols-1)//cols
    sh=Image.new("RGB",(w*cols,h*rows))
    for i,t in enumerate(tiles): sh.paste(t,((i%cols)*w,(i//cols)*h))
    sh.save(Q.S/"all_cond.png"); print(sh.size)
