import{_ as m}from"./KennerligaTable.5747e35a.js";import{u as c}from"./useAxios.31fd1405.js";import{a as p}from"./axios.88f890b6.js";import{A as u,F as t,B as f,U as d,W as _,O as b}from"./index.50837774.js";import"./QSeparator.c70e18de.js";import"./position-engine.daebb3a7.js";import"./QSelect.2b721446.js";const q=u({__name:"GamesList",setup(g){const{data:o,isFinished:r}=c("games",p),s=b(),n=(e,a)=>{s.push({name:"game-detail",params:{id:a.id}})},i={color:"secondary",label:"Spiel",icon:"add_circle",forwardTo:"game-create"},l=[{name:"game",required:!0,align:"left",label:"Spiel",field:e=>e.name,sortable:!0},{name:"platform",label:"Plattform",required:!1,align:"center",field:e=>e.platform,sortable:!0}];return(e,a)=>t(r)?(f(),d(m,{key:0,"create-button":i,flat:"",title:"Spiele",onRowClick:n,rows:t(o),columns:l,"rows-per-page-options":[10,20,50]},null,8,["rows"])):_("",!0)}});export{q as default};
