import{_ as m}from"./KennerligaTable.cf7478e8.js";import{u as c}from"./useAxios.430102b4.js";import{a as p}from"./axios.9876f98e.js";import{L as u,a8 as t,A as f,S as d,a9 as _,N as b}from"./index.5dac4226.js";import"./QSeparator.7043302f.js";import"./position-engine.32f8b7c3.js";import"./QSelect.dd71a04b.js";const y=u({__name:"GamesList",setup(g){const{data:o,isFinished:r}=c("games",p),s=b(),n=(e,a)=>{s.push({name:"game-detail",params:{id:a.id}})},i={color:"secondary",label:"Spiel",icon:"add_circle",forwardTo:"game-create"},l=[{name:"game",required:!0,align:"left",label:"Spiel",field:e=>e.name,sortable:!0},{name:"platform",label:"Plattform",required:!1,align:"center",field:e=>e.platform,sortable:!0}];return(e,a)=>t(r)?(f(),d(m,{key:0,"create-button":i,flat:"",title:"Spiele",onRowClick:n,rows:t(o),columns:l,"rows-per-page-options":[10,20,50]},null,8,["rows"])):_("",!0)}});export{y as default};
