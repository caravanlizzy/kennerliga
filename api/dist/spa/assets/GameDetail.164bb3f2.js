import{u as m}from"./useAxios.a7f2b35e.js";import{a as c}from"./axios.d05b7a47.js";import{G as p,x as t,y as s,S as e,aA as r,T as n,K as u}from"./index.9e72c281.js";const _={key:0,class:"text-h6"},d={key:1,class:"text-h8"},v=p({__name:"GameDetail",setup(l){const i=u(),{data:a,isFinished:o}=m(`games/${i.params.id}`,c);return(f,h)=>(t(),s("div",null,[e(o)?(t(),s("div",_,r(e(a).name),1)):n("",!0),e(o)?(t(),s("div",d,r(e(a).platform),1)):n("",!0)]))}});export{v as default};
