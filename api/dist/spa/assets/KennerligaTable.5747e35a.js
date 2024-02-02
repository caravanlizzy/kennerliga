import{c as A,h as r,d as X,k as yt,J as Ce,g as N,a as u,r as j,w as E,ab as Ie,o as Qe,ac as _t,a7 as qt,e as ze,l as Le,v as Pe,ad as He,ae as Ue,z as De,af as H,a1 as wt,ag as Ee,ah as ke,ai as Me,aj as kt,f as Ke,ak as Ct,a3 as W,Q as J,A as Pt,B as xt,U as Bt,al as Rt,E as Tt,D as Vt}from"./index.50837774.js";import{Q as Ot}from"./QSeparator.c70e18de.js";import{w as Y,x as Z,g as $t}from"./position-engine.daebb3a7.js";import{u as pt,a as Ft,b as Lt,c as Dt,d as We,Q as Et}from"./QSelect.2b721446.js";var Mt=A({name:"QTh",props:{props:Object,autoWidth:Boolean},emits:["click"],setup(e,{slots:a,emit:l}){const c=N(),{proxy:{$q:o}}=c,f=i=>{l("click",i)};return()=>{if(e.props===void 0)return r("th",{class:e.autoWidth===!0?"q-table--col-auto-width":"",onClick:f},X(a.default));let i,d;const v=c.vnode.key;if(v){if(i=e.props.colsMap[v],i===void 0)return}else i=e.props.col;if(i.sortable===!0){const n=i.align==="right"?"unshift":"push";d=yt(a.default,[]),d[n](r(Ce,{class:i.__iconClass,name:o.iconSet.table.arrowUp}))}else d=X(a.default);const m={class:i.__thClass+(e.autoWidth===!0?" q-table--col-auto-width":""),style:i.headerStyle,onClick:n=>{i.sortable===!0&&e.props.sort(i),f(n)}};return r("th",m,d)}}}),jt=A({name:"QList",props:{...Y,bordered:Boolean,dense:Boolean,separator:Boolean,padding:Boolean,tag:{type:String,default:"div"}},setup(e,{slots:a}){const l=N(),c=Z(e,l.proxy.$q),o=u(()=>"q-list"+(e.bordered===!0?" q-list--bordered":"")+(e.dense===!0?" q-list--dense":"")+(e.separator===!0?" q-list--separator":"")+(c.value===!0?" q-list--dark":"")+(e.padding===!0?" q-list--padding":""));return()=>r(e.tag,{class:o.value},X(a.default))}});const At=["horizontal","vertical","cell","none"];var Nt=A({name:"QMarkupTable",props:{...Y,dense:Boolean,flat:Boolean,bordered:Boolean,square:Boolean,wrapCells:Boolean,separator:{type:String,default:"horizontal",validator:e=>At.includes(e)}},setup(e,{slots:a}){const l=N(),c=Z(e,l.proxy.$q),o=u(()=>`q-markup-table q-table__container q-table__card q-table--${e.separator}-separator`+(c.value===!0?" q-table--dark q-table__card--dark q-dark":"")+(e.dense===!0?" q-table--dense":"")+(e.flat===!0?" q-table--flat":"")+(e.bordered===!0?" q-table--bordered":"")+(e.square===!0?" q-table--square":"")+(e.wrapCells===!1?" q-table--no-wrap":""));return()=>r("div",{class:o.value},[r("table",{class:"q-table"},X(a.default))])}});function Ge(e,a){return r("div",e,[r("table",{class:"q-table"},a)])}const It={list:jt,table:Nt},Qt=["list","table","__qtable"];var zt=A({name:"QVirtualScroll",props:{...pt,type:{type:String,default:"list",validator:e=>Qt.includes(e)},items:{type:Array,default:()=>[]},itemsFn:Function,itemsSize:Number,scrollTarget:{default:void 0}},setup(e,{slots:a,attrs:l}){let c;const o=j(null),f=u(()=>e.itemsSize>=0&&e.itemsFn!==void 0?parseInt(e.itemsSize,10):Array.isArray(e.items)?e.items.length:0),{virtualScrollSliceRange:i,localResetVirtualScroll:d,padVirtualScroll:v,onVirtualScrollEvt:m}=Ft({virtualScrollLength:f,getVirtualScrollTarget:q,getVirtualScrollEl:k}),n=u(()=>{if(f.value===0)return[];const V=($,x)=>({index:i.value.from+x,item:$});return e.itemsFn===void 0?e.items.slice(i.value.from,i.value.to).map(V):e.itemsFn(i.value.from,i.value.to-i.value.from).map(V)}),b=u(()=>"q-virtual-scroll q-virtual-scroll"+(e.virtualScrollHorizontal===!0?"--horizontal":"--vertical")+(e.scrollTarget!==void 0?"":" scroll")),w=u(()=>e.scrollTarget!==void 0?{}:{tabindex:0});E(f,()=>{d()}),E(()=>e.scrollTarget,()=>{h(),y()});function k(){return o.value.$el||o.value}function q(){return c}function y(){c=$t(k(),e.scrollTarget),c.addEventListener("scroll",m,Le.passive)}function h(){c!==void 0&&(c.removeEventListener("scroll",m,Le.passive),c=void 0)}function T(){let V=v(e.type==="list"?"div":"tbody",n.value.map(a.default));return a.before!==void 0&&(V=a.before().concat(V)),Pe(a.after,V)}return Ie(()=>{d()}),Qe(()=>{y()}),_t(()=>{y()}),qt(()=>{h()}),ze(()=>{h()}),()=>{if(a.default===void 0){console.error("QVirtualScroll: default scoped slot is required for rendering");return}return e.type==="__qtable"?Ge({ref:o,class:"q-table__middle "+b.value},T()):r(It[e.type],{...l,ref:o,class:[l.class,b.value],...w.value},T)}}});const Ht={xs:2,sm:4,md:6,lg:10,xl:14};function je(e,a,l){return{transform:a===!0?`translateX(${l.lang.rtl===!0?"-":""}100%) scale3d(${-e},1,1)`:`scale3d(${e},1,1)`}}var Ut=A({name:"QLinearProgress",props:{...Y,...He,value:{type:Number,default:0},buffer:Number,color:String,trackColor:String,reverse:Boolean,stripe:Boolean,indeterminate:Boolean,query:Boolean,rounded:Boolean,animationSpeed:{type:[String,Number],default:2100},instantFeedback:Boolean},setup(e,{slots:a}){const{proxy:l}=N(),c=Z(e,l.$q),o=Ue(e,Ht),f=u(()=>e.indeterminate===!0||e.query===!0),i=u(()=>e.reverse!==e.query),d=u(()=>({...o.value!==null?o.value:{},"--q-linear-progress-speed":`${e.animationSpeed}ms`})),v=u(()=>"q-linear-progress"+(e.color!==void 0?` text-${e.color}`:"")+(e.reverse===!0||e.query===!0?" q-linear-progress--reverse":"")+(e.rounded===!0?" rounded-borders":"")),m=u(()=>je(e.buffer!==void 0?e.buffer:1,i.value,l.$q)),n=u(()=>`with${e.instantFeedback===!0?"out":""}-transition`),b=u(()=>`q-linear-progress__track absolute-full q-linear-progress__track--${n.value} q-linear-progress__track--${c.value===!0?"dark":"light"}`+(e.trackColor!==void 0?` bg-${e.trackColor}`:"")),w=u(()=>je(f.value===!0?1:e.value,i.value,l.$q)),k=u(()=>`q-linear-progress__model absolute-full q-linear-progress__model--${n.value} q-linear-progress__model--${f.value===!0?"in":""}determinate`),q=u(()=>({width:`${e.value*100}%`})),y=u(()=>`q-linear-progress__stripe absolute-${e.reverse===!0?"right":"left"} q-linear-progress__stripe--${n.value}`);return()=>{const h=[r("div",{class:b.value,style:m.value}),r("div",{class:k.value,style:w.value})];return e.stripe===!0&&f.value===!1&&h.push(r("div",{class:y.value,style:q.value})),r("div",{class:v.value,style:d.value,role:"progressbar","aria-valuemin":0,"aria-valuemax":1,"aria-valuenow":e.indeterminate===!0?void 0:e.value},Pe(a.default,h))}}});function Kt(e,a){const l=j(null),c=u(()=>e.disable===!0?null:r("span",{ref:l,class:"no-outline",tabindex:-1}));function o(f){const i=a.value;f!==void 0&&f.type.indexOf("key")===0?i!==null&&document.activeElement!==i&&i.contains(document.activeElement)===!0&&i.focus():l.value!==null&&(f===void 0||i!==null&&i.contains(f.target)===!0)&&l.value.focus()}return{refocusTargetEl:c,refocusTarget:o}}var Wt={xs:30,sm:35,md:40,lg:50,xl:60};const Gt={...Y,...He,...Lt,modelValue:{required:!0,default:null},val:{},trueValue:{default:!0},falseValue:{default:!1},indeterminateValue:{default:null},checkedIcon:String,uncheckedIcon:String,indeterminateIcon:String,toggleOrder:{type:String,validator:e=>e==="tf"||e==="ft"},toggleIndeterminate:Boolean,label:String,leftLabel:Boolean,color:String,keepColor:Boolean,dense:Boolean,disable:Boolean,tabindex:[String,Number]},Jt=["update:modelValue"];function Xt(e,a){const{props:l,slots:c,emit:o,proxy:f}=N(),{$q:i}=f,d=Z(l,i),v=j(null),{refocusTargetEl:m,refocusTarget:n}=Kt(l,v),b=Ue(l,Wt),w=u(()=>l.val!==void 0&&Array.isArray(l.modelValue)),k=u(()=>{const C=H(l.val);return w.value===!0?l.modelValue.findIndex(F=>H(F)===C):-1}),q=u(()=>w.value===!0?k.value>-1:H(l.modelValue)===H(l.trueValue)),y=u(()=>w.value===!0?k.value===-1:H(l.modelValue)===H(l.falseValue)),h=u(()=>q.value===!1&&y.value===!1),T=u(()=>l.disable===!0?-1:l.tabindex||0),V=u(()=>`q-${e} cursor-pointer no-outline row inline no-wrap items-center`+(l.disable===!0?" disabled":"")+(d.value===!0?` q-${e}--dark`:"")+(l.dense===!0?` q-${e}--dense`:"")+(l.leftLabel===!0?" reverse":"")),$=u(()=>{const C=q.value===!0?"truthy":y.value===!0?"falsy":"indet",F=l.color!==void 0&&(l.keepColor===!0||(e==="toggle"?q.value===!0:y.value!==!0))?` text-${l.color}`:"";return`q-${e}__inner relative-position non-selectable q-${e}__inner--${C}${F}`}),x=u(()=>{const C={type:"checkbox"};return l.name!==void 0&&Object.assign(C,{".checked":q.value,"^checked":q.value===!0?"checked":void 0,name:l.name,value:w.value===!0?l.val:l.trueValue}),C}),R=Dt(x),I=u(()=>{const C={tabindex:T.value,role:e==="toggle"?"switch":"checkbox","aria-label":l.label,"aria-checked":h.value===!0?"mixed":q.value===!0?"true":"false"};return l.disable===!0&&(C["aria-disabled"]="true"),C});function U(C){C!==void 0&&(De(C),n(C)),l.disable!==!0&&o("update:modelValue",K(),C)}function K(){if(w.value===!0){if(q.value===!0){const C=l.modelValue.slice();return C.splice(k.value,1),C}return l.modelValue.concat([l.val])}if(q.value===!0){if(l.toggleOrder!=="ft"||l.toggleIndeterminate===!1)return l.falseValue}else if(y.value===!0){if(l.toggleOrder==="ft"||l.toggleIndeterminate===!1)return l.trueValue}else return l.toggleOrder!=="ft"?l.trueValue:l.falseValue;return l.indeterminateValue}function ee(C){(C.keyCode===13||C.keyCode===32)&&De(C)}function p(C){(C.keyCode===13||C.keyCode===32)&&U(C)}const M=a(q,h);return Object.assign(f,{toggle:U}),()=>{const C=M();l.disable!==!0&&R(C,"unshift",` q-${e}__native absolute q-ma-none q-pa-none`);const F=[r("div",{class:$.value,style:b.value,"aria-hidden":"true"},C)];m.value!==null&&F.push(m.value);const te=l.label!==void 0?Pe(c.default,[l.label]):X(c.default);return te!==void 0&&F.push(r("div",{class:`q-${e}__label q-anchor--skip`},te)),r("div",{ref:v,class:V.value,...I.value,onClick:U,onKeydown:ee,onKeyup:p},F)}}const Yt=r("div",{key:"svg",class:"q-checkbox__bg absolute"},[r("svg",{class:"q-checkbox__svg fit absolute-full",viewBox:"0 0 24 24"},[r("path",{class:"q-checkbox__truthy",fill:"none",d:"M1.73,12.91 8.1,19.28 22.79,4.59"}),r("path",{class:"q-checkbox__indet",d:"M4,14H20V10H4"})])]);var we=A({name:"QCheckbox",props:Gt,emits:Jt,setup(e){function a(l,c){const o=u(()=>(l.value===!0?e.checkedIcon:c.value===!0?e.indeterminateIcon:e.uncheckedIcon)||null);return()=>o.value!==null?[r("div",{key:"icon",class:"q-checkbox__icon-container absolute-full flex flex-center no-wrap"},[r(Ce,{class:"q-checkbox__icon",name:o.value})])]:[Yt]}return Xt("checkbox",a)}});let G=0;const Zt={fullscreen:Boolean,noRouteFullscreenExit:Boolean},el=["update:fullscreen","fullscreen"];function tl(){const e=N(),{props:a,emit:l,proxy:c}=e;let o,f,i;const d=j(!1);wt(e)===!0&&E(()=>c.$route.fullPath,()=>{a.noRouteFullscreenExit!==!0&&n()}),E(()=>a.fullscreen,b=>{d.value!==b&&v()}),E(d,b=>{l("update:fullscreen",b),l("fullscreen",b)});function v(){d.value===!0?n():m()}function m(){d.value!==!0&&(d.value=!0,i=c.$el.parentNode,i.replaceChild(f,c.$el),document.body.appendChild(c.$el),G++,G===1&&document.body.classList.add("q-body--fullscreen-mixin"),o={handler:n},Ee.add(o))}function n(){d.value===!0&&(o!==void 0&&(Ee.remove(o),o=void 0),i.replaceChild(c.$el,f),d.value=!1,G=Math.max(0,G-1),G===0&&(document.body.classList.remove("q-body--fullscreen-mixin"),c.$el.scrollIntoView!==void 0&&setTimeout(()=>{c.$el.scrollIntoView()})))}return Ie(()=>{f=document.createElement("span")}),Qe(()=>{a.fullscreen===!0&&m()}),ze(n),Object.assign(c,{toggleFullscreen:v,setFullscreen:m,exitFullscreen:n}),{inFullscreen:d,toggleFullscreen:v}}function ll(e,a){return new Date(e)-new Date(a)}const al={sortMethod:Function,binaryStateSort:Boolean,columnSortOrder:{type:String,validator:e=>e==="ad"||e==="da",default:"ad"}};function nl(e,a,l,c){const o=u(()=>{const{sortBy:d}=a.value;return d&&l.value.find(v=>v.name===d)||null}),f=u(()=>e.sortMethod!==void 0?e.sortMethod:(d,v,m)=>{const n=l.value.find(k=>k.name===v);if(n===void 0||n.field===void 0)return d;const b=m===!0?-1:1,w=typeof n.field=="function"?k=>n.field(k):k=>k[n.field];return d.sort((k,q)=>{let y=w(k),h=w(q);return n.rawSort!==void 0?n.rawSort(y,h,k,q)*b:y==null?-1*b:h==null?1*b:n.sort!==void 0?n.sort(y,h,k,q)*b:ke(y)===!0&&ke(h)===!0?(y-h)*b:Me(y)===!0&&Me(h)===!0?ll(y,h)*b:typeof y=="boolean"&&typeof h=="boolean"?(y-h)*b:([y,h]=[y,h].map(T=>(T+"").toLocaleString().toLowerCase()),y<h?-1*b:y===h?0:b)})});function i(d){let v=e.columnSortOrder;if(kt(d)===!0)d.sortOrder&&(v=d.sortOrder),d=d.name;else{const b=l.value.find(w=>w.name===d);b!==void 0&&b.sortOrder&&(v=b.sortOrder)}let{sortBy:m,descending:n}=a.value;m!==d?(m=d,n=v==="da"):e.binaryStateSort===!0?n=!n:n===!0?v==="ad"?m=null:n=!1:v==="ad"?n=!0:m=null,c({sortBy:m,descending:n,page:1})}return{columnToSort:o,computedSortMethod:f,sort:i}}const rl={filter:[String,Object],filterMethod:Function};function ol(e,a){const l=u(()=>e.filterMethod!==void 0?e.filterMethod:(c,o,f,i)=>{const d=o?o.toLowerCase():"";return c.filter(v=>f.some(m=>{const n=i(m,v)+"";return(n==="undefined"||n==="null"?"":n.toLowerCase()).indexOf(d)!==-1}))});return E(()=>e.filter,()=>{Ke(()=>{a({page:1},!0)})},{deep:!0}),{computedFilterMethod:l}}function il(e,a){for(const l in a)if(a[l]!==e[l])return!1;return!0}function Ae(e){return e.page<1&&(e.page=1),e.rowsPerPage!==void 0&&e.rowsPerPage<1&&(e.rowsPerPage=0),e}const ul={pagination:Object,rowsPerPageOptions:{type:Array,default:()=>[5,7,10,15,20,25,50,0]},"onUpdate:pagination":[Function,Array]};function sl(e,a){const{props:l,emit:c}=e,o=j(Object.assign({sortBy:null,descending:!1,page:1,rowsPerPage:l.rowsPerPageOptions.length!==0?l.rowsPerPageOptions[0]:5},l.pagination)),f=u(()=>{const n=l["onUpdate:pagination"]!==void 0?{...o.value,...l.pagination}:o.value;return Ae(n)}),i=u(()=>f.value.rowsNumber!==void 0);function d(n){v({pagination:n,filter:l.filter})}function v(n={}){Ke(()=>{c("request",{pagination:n.pagination||f.value,filter:n.filter||l.filter,getCellValue:a})})}function m(n,b){const w=Ae({...f.value,...n});if(il(f.value,w)===!0){i.value===!0&&b===!0&&d(w);return}if(i.value===!0){d(w);return}l.pagination!==void 0&&l["onUpdate:pagination"]!==void 0?c("update:pagination",w):o.value=w}return{innerPagination:o,computedPagination:f,isServerSide:i,requestServerInteraction:v,setPagination:m}}function cl(e,a,l,c,o,f){const{props:i,emit:d,proxy:{$q:v}}=e,m=u(()=>c.value===!0?l.value.rowsNumber||0:f.value),n=u(()=>{const{page:x,rowsPerPage:R}=l.value;return(x-1)*R}),b=u(()=>{const{page:x,rowsPerPage:R}=l.value;return x*R}),w=u(()=>l.value.page===1),k=u(()=>l.value.rowsPerPage===0?1:Math.max(1,Math.ceil(m.value/l.value.rowsPerPage))),q=u(()=>b.value===0?!0:l.value.page>=k.value),y=u(()=>(i.rowsPerPageOptions.includes(a.value.rowsPerPage)?i.rowsPerPageOptions:[a.value.rowsPerPage].concat(i.rowsPerPageOptions)).map(R=>({label:R===0?v.lang.table.allRows:""+R,value:R})));E(k,(x,R)=>{if(x===R)return;const I=l.value.page;x&&!I?o({page:1}):x<I&&o({page:x})});function h(){o({page:1})}function T(){const{page:x}=l.value;x>1&&o({page:x-1})}function V(){const{page:x,rowsPerPage:R}=l.value;b.value>0&&x*R<m.value&&o({page:x+1})}function $(){o({page:k.value})}return i["onUpdate:pagination"]!==void 0&&d("update:pagination",{...l.value}),{firstRowIndex:n,lastRowIndex:b,isFirstPage:w,isLastPage:q,pagesNumber:k,computedRowsPerPageOptions:y,computedRowsNumber:m,firstPage:h,prevPage:T,nextPage:V,lastPage:$}}const dl={selection:{type:String,default:"none",validator:e=>["single","multiple","none"].includes(e)},selected:{type:Array,default:()=>[]}},vl=["update:selected","selection"];function fl(e,a,l,c){const o=u(()=>{const q={};return e.selected.map(c.value).forEach(y=>{q[y]=!0}),q}),f=u(()=>e.selection!=="none"),i=u(()=>e.selection==="single"),d=u(()=>e.selection==="multiple"),v=u(()=>l.value.length!==0&&l.value.every(q=>o.value[c.value(q)]===!0)),m=u(()=>v.value!==!0&&l.value.some(q=>o.value[c.value(q)]===!0)),n=u(()=>e.selected.length);function b(q){return o.value[q]===!0}function w(){a("update:selected",[])}function k(q,y,h,T){a("selection",{rows:y,added:h,keys:q,evt:T});const V=i.value===!0?h===!0?y:[]:h===!0?e.selected.concat(y):e.selected.filter($=>q.includes(c.value($))===!1);a("update:selected",V)}return{hasSelectionMode:f,singleSelection:i,multipleSelection:d,allRowsSelected:v,someRowsSelected:m,rowsSelectedNumber:n,isRowSelected:b,clearSelection:w,updateSelection:k}}function Ne(e){return Array.isArray(e)?e.slice():[]}const gl={expanded:Array},bl=["update:expanded"];function ml(e,a){const l=j(Ne(e.expanded));E(()=>e.expanded,i=>{l.value=Ne(i)});function c(i){return l.value.includes(i)}function o(i){e.expanded!==void 0?a("update:expanded",i):l.value=i}function f(i,d){const v=l.value.slice(),m=v.indexOf(i);d===!0?m===-1&&(v.push(i),o(v)):m!==-1&&(v.splice(m,1),o(v))}return{isRowExpanded:c,setExpanded:o,updateExpanded:f}}const Sl={visibleColumns:Array};function hl(e,a,l){const c=u(()=>{if(e.columns!==void 0)return e.columns;const d=e.rows[0];return d!==void 0?Object.keys(d).map(v=>({name:v,label:v.toUpperCase(),field:v,align:ke(d[v])?"right":"left",sortable:!0})):[]}),o=u(()=>{const{sortBy:d,descending:v}=a.value;return(e.visibleColumns!==void 0?c.value.filter(n=>n.required===!0||e.visibleColumns.includes(n.name)===!0):c.value).map(n=>{const b=n.align||"right",w=`text-${b}`;return{...n,align:b,__iconClass:`q-table__sort-icon q-table__sort-icon--${b}`,__thClass:w+(n.headerClasses!==void 0?" "+n.headerClasses:"")+(n.sortable===!0?" sortable":"")+(n.name===d?` sorted ${v===!0?"sort-desc":""}`:""),__tdStyle:n.style!==void 0?typeof n.style!="function"?()=>n.style:n.style:()=>null,__tdClass:n.classes!==void 0?typeof n.classes!="function"?()=>w+" "+n.classes:k=>w+" "+n.classes(k):()=>w}})}),f=u(()=>{const d={};return o.value.forEach(v=>{d[v.name]=v}),d}),i=u(()=>e.tableColspan!==void 0?e.tableColspan:o.value.length+(l.value===!0?1:0));return{colList:c,computedCols:o,computedColsMap:f,computedColspan:i}}const ce="q-table__bottom row items-center",Je={};We.forEach(e=>{Je[e]={}});var yl=A({name:"QTable",props:{rows:{type:Array,default:()=>[]},rowKey:{type:[String,Function],default:"id"},columns:Array,loading:Boolean,iconFirstPage:String,iconPrevPage:String,iconNextPage:String,iconLastPage:String,title:String,hideHeader:Boolean,grid:Boolean,gridHeader:Boolean,dense:Boolean,flat:Boolean,bordered:Boolean,square:Boolean,separator:{type:String,default:"horizontal",validator:e=>["horizontal","vertical","cell","none"].includes(e)},wrapCells:Boolean,virtualScroll:Boolean,virtualScrollTarget:{default:void 0},...Je,noDataLabel:String,noResultsLabel:String,loadingLabel:String,selectedRowsLabel:Function,rowsPerPageLabel:String,paginationLabel:Function,color:{type:String,default:"grey-8"},titleClass:[String,Array,Object],tableStyle:[String,Array,Object],tableClass:[String,Array,Object],tableHeaderStyle:[String,Array,Object],tableHeaderClass:[String,Array,Object],cardContainerClass:[String,Array,Object],cardContainerStyle:[String,Array,Object],cardStyle:[String,Array,Object],cardClass:[String,Array,Object],hideBottom:Boolean,hideSelectedBanner:Boolean,hideNoData:Boolean,hidePagination:Boolean,onRowClick:Function,onRowDblclick:Function,onRowContextmenu:Function,...Y,...Zt,...Sl,...rl,...ul,...gl,...dl,...al},emits:["request","virtualScroll",...el,...bl,...vl],setup(e,{slots:a,emit:l}){const c=N(),{proxy:{$q:o}}=c,f=Z(e,o),{inFullscreen:i,toggleFullscreen:d}=tl(),v=u(()=>typeof e.rowKey=="function"?e.rowKey:t=>t[e.rowKey]),m=j(null),n=j(null),b=u(()=>e.grid!==!0&&e.virtualScroll===!0),w=u(()=>" q-table__card"+(f.value===!0?" q-table__card--dark q-dark":"")+(e.square===!0?" q-table--square":"")+(e.flat===!0?" q-table--flat":"")+(e.bordered===!0?" q-table--bordered":"")),k=u(()=>`q-table__container q-table--${e.separator}-separator column no-wrap`+(e.grid===!0?" q-table--grid":w.value)+(f.value===!0?" q-table--dark":"")+(e.dense===!0?" q-table--dense":"")+(e.wrapCells===!1?" q-table--no-wrap":"")+(i.value===!0?" fullscreen scroll":"")),q=u(()=>k.value+(e.loading===!0?" q-table--loading":""));E(()=>e.tableStyle+e.tableClass+e.tableHeaderStyle+e.tableHeaderClass+k.value,()=>{b.value===!0&&n.value!==null&&n.value.reset()});const{innerPagination:y,computedPagination:h,isServerSide:T,requestServerInteraction:V,setPagination:$}=sl(c,Q),{computedFilterMethod:x}=ol(e,$),{isRowExpanded:R,setExpanded:I,updateExpanded:U}=ml(e,l),K=u(()=>{let t=e.rows;if(T.value===!0||t.length===0)return t;const{sortBy:s,descending:g}=h.value;return e.filter&&(t=x.value(t,e.filter,L.value,Q)),Ze.value!==null&&(t=et.value(e.rows===t?t.slice():t,s,g)),t}),ee=u(()=>K.value.length),p=u(()=>{let t=K.value;if(T.value===!0)return t;const{rowsPerPage:s}=h.value;return s!==0&&(ae.value===0&&e.rows!==t?t.length>ne.value&&(t=t.slice(0,ne.value)):t=t.slice(ae.value,ne.value)),t}),{hasSelectionMode:M,singleSelection:C,multipleSelection:F,allRowsSelected:te,someRowsSelected:xe,rowsSelectedNumber:de,isRowSelected:ve,clearSelection:Xe,updateSelection:le}=fl(e,l,p,v),{colList:Ye,computedCols:L,computedColsMap:Be,computedColspan:Re}=hl(e,h,M),{columnToSort:Ze,computedSortMethod:et,sort:fe}=nl(e,h,Ye,$),{firstRowIndex:ae,lastRowIndex:ne,isFirstPage:ge,isLastPage:be,pagesNumber:re,computedRowsPerPageOptions:tt,computedRowsNumber:oe,firstPage:me,prevPage:Se,nextPage:he,lastPage:ye}=cl(c,y,h,T,$,ee),lt=u(()=>p.value.length===0),at=u(()=>{const t={};return We.forEach(s=>{t[s]=e[s]}),t.virtualScrollItemSize===void 0&&(t.virtualScrollItemSize=e.dense===!0?28:48),t});function nt(){b.value===!0&&n.value.reset()}function rt(){if(e.grid===!0)return St();const t=e.hideHeader!==!0?pe:null;if(b.value===!0){const g=a["top-row"],S=a["bottom-row"],_={default:B=>Ve(B.item,a.body,B.index)};if(g!==void 0){const B=r("tbody",g({cols:L.value}));_.before=t===null?()=>B:()=>[t()].concat(B)}else t!==null&&(_.before=t);return S!==void 0&&(_.after=()=>r("tbody",S({cols:L.value}))),r(zt,{ref:n,class:e.tableClass,style:e.tableStyle,...at.value,scrollTarget:e.virtualScrollTarget,items:p.value,type:"__qtable",tableColspan:Re.value,onVirtualScroll:it},_)}const s=[ut()];return t!==null&&s.unshift(t()),Ge({class:["q-table__middle scroll",e.tableClass],style:e.tableStyle},s)}function ot(t,s){if(n.value!==null){n.value.scrollTo(t,s);return}t=parseInt(t,10);const g=m.value.querySelector(`tbody tr:nth-of-type(${t+1})`);if(g!==null){const S=m.value.querySelector(".q-table__middle.scroll"),_=g.offsetTop-e.virtualScrollStickySizeStart,B=_<S.scrollTop?"decrease":"increase";S.scrollTop=_,l("virtualScroll",{index:t,from:0,to:y.value.rowsPerPage-1,direction:B})}}function it(t){l("virtualScroll",t)}function Te(){return[r(Ut,{class:"q-table__linear-progress",color:e.color,dark:f.value,indeterminate:!0,trackColor:"transparent"})]}function Ve(t,s,g){const S=v.value(t),_=ve(S);if(s!==void 0)return s(Oe({key:S,row:t,pageIndex:g,__trClass:_?"selected":""}));const B=a["body-cell"],P=L.value.map(O=>{const ue=a[`body-cell-${O.name}`],se=ue!==void 0?ue:B;return se!==void 0?se(st({key:S,row:t,pageIndex:g,col:O})):r("td",{class:O.__tdClass(t),style:O.__tdStyle(t)},Q(O,t))});if(M.value===!0){const O=a["body-selection"],ue=O!==void 0?O(ct({key:S,row:t,pageIndex:g})):[r(we,{modelValue:_,color:e.color,dark:f.value,dense:e.dense,"onUpdate:modelValue":(se,ht)=>{le([S],[t],se,ht)}})];P.unshift(r("td",{class:"q-table--col-auto-width"},ue))}const D={key:S,class:{selected:_}};return e.onRowClick!==void 0&&(D.class["cursor-pointer"]=!0,D.onClick=O=>{l("RowClick",O,t,g)}),e.onRowDblclick!==void 0&&(D.class["cursor-pointer"]=!0,D.onDblclick=O=>{l("RowDblclick",O,t,g)}),e.onRowContextmenu!==void 0&&(D.class["cursor-pointer"]=!0,D.onContextmenu=O=>{l("RowContextmenu",O,t,g)}),r("tr",D,P)}function ut(){const t=a.body,s=a["top-row"],g=a["bottom-row"];let S=p.value.map((_,B)=>Ve(_,t,B));return s!==void 0&&(S=s({cols:L.value}).concat(S)),g!==void 0&&(S=S.concat(g({cols:L.value}))),r("tbody",S)}function Oe(t){return _e(t),t.cols=t.cols.map(s=>W({...s},"value",()=>Q(s,t.row))),t}function st(t){return _e(t),W(t,"value",()=>Q(t.col,t.row)),t}function ct(t){return _e(t),t}function _e(t){Object.assign(t,{cols:L.value,colsMap:Be.value,sort:fe,rowIndex:ae.value+t.pageIndex,color:e.color,dark:f.value,dense:e.dense}),M.value===!0&&W(t,"selected",()=>ve(t.key),(s,g)=>{le([t.key],[t.row],s,g)}),W(t,"expand",()=>R(t.key),s=>{U(t.key,s)})}function Q(t,s){const g=typeof t.field=="function"?t.field(s):s[t.field];return t.format!==void 0?t.format(g,s):g}const z=u(()=>({pagination:h.value,pagesNumber:re.value,isFirstPage:ge.value,isLastPage:be.value,firstPage:me,prevPage:Se,nextPage:he,lastPage:ye,inFullscreen:i.value,toggleFullscreen:d}));function dt(){const t=a.top,s=a["top-left"],g=a["top-right"],S=a["top-selection"],_=M.value===!0&&S!==void 0&&de.value>0,B="q-table__top relative-position row items-center";if(t!==void 0)return r("div",{class:B},[t(z.value)]);let P;if(_===!0?P=S(z.value).slice():(P=[],s!==void 0?P.push(r("div",{class:"q-table__control"},[s(z.value)])):e.title&&P.push(r("div",{class:"q-table__control"},[r("div",{class:["q-table__title",e.titleClass]},e.title)]))),g!==void 0&&(P.push(r("div",{class:"q-table__separator col"})),P.push(r("div",{class:"q-table__control"},[g(z.value)]))),P.length!==0)return r("div",{class:B},P)}const $e=u(()=>xe.value===!0?null:te.value);function pe(){const t=vt();return e.loading===!0&&a.loading===void 0&&t.push(r("tr",{class:"q-table__progress"},[r("th",{class:"relative-position",colspan:Re.value},Te())])),r("thead",t)}function vt(){const t=a.header,s=a["header-cell"];if(t!==void 0)return t(qe({header:!0})).slice();const g=L.value.map(S=>{const _=a[`header-cell-${S.name}`],B=_!==void 0?_:s,P=qe({col:S});return B!==void 0?B(P):r(Mt,{key:S.name,props:P},()=>S.label)});if(C.value===!0&&e.grid!==!0)g.unshift(r("th",{class:"q-table--col-auto-width"}," "));else if(F.value===!0){const S=a["header-selection"],_=S!==void 0?S(qe({})):[r(we,{color:e.color,modelValue:$e.value,dark:f.value,dense:e.dense,"onUpdate:modelValue":Fe})];g.unshift(r("th",{class:"q-table--col-auto-width"},_))}return[r("tr",{class:e.tableHeaderClass,style:e.tableHeaderStyle},g)]}function qe(t){return Object.assign(t,{cols:L.value,sort:fe,colsMap:Be.value,color:e.color,dark:f.value,dense:e.dense}),F.value===!0&&W(t,"selected",()=>$e.value,Fe),t}function Fe(t){xe.value===!0&&(t=!1),le(p.value.map(v.value),p.value,t)}const ie=u(()=>{const t=[e.iconFirstPage||o.iconSet.table.firstPage,e.iconPrevPage||o.iconSet.table.prevPage,e.iconNextPage||o.iconSet.table.nextPage,e.iconLastPage||o.iconSet.table.lastPage];return o.lang.rtl===!0?t.reverse():t});function ft(){if(e.hideBottom===!0)return;if(lt.value===!0){if(e.hideNoData===!0)return;const g=e.loading===!0?e.loadingLabel||o.lang.table.loading:e.filter?e.noResultsLabel||o.lang.table.noResults:e.noDataLabel||o.lang.table.noData,S=a["no-data"],_=S!==void 0?[S({message:g,icon:o.iconSet.table.warning,filter:e.filter})]:[r(Ce,{class:"q-table__bottom-nodata-icon",name:o.iconSet.table.warning}),g];return r("div",{class:ce+" q-table__bottom--nodata"},_)}const t=a.bottom;if(t!==void 0)return r("div",{class:ce},[t(z.value)]);const s=e.hideSelectedBanner!==!0&&M.value===!0&&de.value>0?[r("div",{class:"q-table__control"},[r("div",[(e.selectedRowsLabel||o.lang.table.selectedRecords)(de.value)])])]:[];if(e.hidePagination!==!0)return r("div",{class:ce+" justify-end"},bt(s));if(s.length!==0)return r("div",{class:ce},s)}function gt(t){$({page:1,rowsPerPage:t.value})}function bt(t){let s;const{rowsPerPage:g}=h.value,S=e.paginationLabel||o.lang.table.pagination,_=a.pagination,B=e.rowsPerPageOptions.length>1;if(t.push(r("div",{class:"q-table__separator col"})),B===!0&&t.push(r("div",{class:"q-table__control"},[r("span",{class:"q-table__bottom-item"},[e.rowsPerPageLabel||o.lang.table.recordsPerPage]),r(Et,{class:"q-table__select inline q-table__bottom-item",color:e.color,modelValue:g,options:tt.value,displayValue:g===0?o.lang.table.allRows:g,dark:f.value,borderless:!0,dense:!0,optionsDense:!0,optionsCover:!0,"onUpdate:modelValue":gt})])),_!==void 0)s=_(z.value);else if(s=[r("span",g!==0?{class:"q-table__bottom-item"}:{},[g?S(ae.value+1,Math.min(ne.value,oe.value),oe.value):S(1,ee.value,oe.value)])],g!==0&&re.value>1){const P={color:e.color,round:!0,dense:!0,flat:!0};e.dense===!0&&(P.size="sm"),re.value>2&&s.push(r(J,{key:"pgFirst",...P,icon:ie.value[0],disable:ge.value,onClick:me})),s.push(r(J,{key:"pgPrev",...P,icon:ie.value[1],disable:ge.value,onClick:Se}),r(J,{key:"pgNext",...P,icon:ie.value[2],disable:be.value,onClick:he})),re.value>2&&s.push(r(J,{key:"pgLast",...P,icon:ie.value[3],disable:be.value,onClick:ye}))}return t.push(r("div",{class:"q-table__control"},s)),t}function mt(){const t=e.gridHeader===!0?[r("table",{class:"q-table"},[pe()])]:e.loading===!0&&a.loading===void 0?Te():void 0;return r("div",{class:"q-table__middle"},t)}function St(){const t=a.item!==void 0?a.item:s=>{const g=s.cols.map(_=>r("div",{class:"q-table__grid-item-row"},[r("div",{class:"q-table__grid-item-title"},[_.label]),r("div",{class:"q-table__grid-item-value"},[_.value])]));if(M.value===!0){const _=a["body-selection"],B=_!==void 0?_(s):[r(we,{modelValue:s.selected,color:e.color,dark:f.value,dense:e.dense,"onUpdate:modelValue":(P,D)=>{le([s.key],[s.row],P,D)}})];g.unshift(r("div",{class:"q-table__grid-item-row"},B),r(Ot,{dark:f.value}))}const S={class:["q-table__grid-item-card"+w.value,e.cardClass],style:e.cardStyle};return(e.onRowClick!==void 0||e.onRowDblclick!==void 0)&&(S.class[0]+=" cursor-pointer",e.onRowClick!==void 0&&(S.onClick=_=>{l("RowClick",_,s.row,s.pageIndex)}),e.onRowDblclick!==void 0&&(S.onDblclick=_=>{l("RowDblclick",_,s.row,s.pageIndex)})),r("div",{class:"q-table__grid-item col-xs-12 col-sm-6 col-md-4 col-lg-3"+(s.selected===!0?" q-table__grid-item--selected":"")},[r("div",S,g)])};return r("div",{class:["q-table__grid-content row",e.cardContainerClass],style:e.cardContainerStyle},p.value.map((s,g)=>t(Oe({key:v.value(s),row:s,pageIndex:g}))))}return Object.assign(c.proxy,{requestServerInteraction:V,setPagination:$,firstPage:me,prevPage:Se,nextPage:he,lastPage:ye,isRowSelected:ve,clearSelection:Xe,isRowExpanded:R,setExpanded:I,sort:fe,resetVirtualScroll:nt,scrollTo:ot,getCellValue:Q}),Ct(c.proxy,{filteredSortedRows:()=>K.value,computedRows:()=>p.value,computedRowsNumber:()=>oe.value}),()=>{const t=[dt()],s={ref:m,class:q.value};return e.grid===!0?t.push(mt()):Object.assign(s,{class:[s.class,e.cardClass],style:e.cardStyle}),t.push(rt(),ft()),e.loading===!0&&a.loading!==void 0&&t.push(a.loading()),r("div",s,t)}}});const Cl=Pt({__name:"KennerligaTable",props:{createButton:{}},setup(e){return(a,l)=>(xt(),Bt(yl,{"card-class":"bg-primary text-grey-3","table-header-class":"text-info",dark:"",flat:"","rows-per-page-options":[10,20,50]},Rt({_:2},[a.createButton?{name:"top-right",fn:Tt(()=>[Vt(J,{outline:"",color:a.createButton.color,to:{name:a.createButton.forwardTo},icon:a.createButton.icon,label:a.createButton.label},null,8,["color","to","icon","label"])]),key:"0"}:void 0]),1024))}});export{Cl as _};
