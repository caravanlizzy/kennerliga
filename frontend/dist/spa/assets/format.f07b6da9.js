import{u as M,a as W}from"./use-dark.0291611e.js";import{c as T,a as d,h as p,g as k,d as z,a4 as G,a5 as R,X as J,Y as Z,r as A,a6 as ee,K as j,k as te,a7 as le,w as I,a8 as oe,o as ie,f as D,a9 as ne,e as F,aa as ae,ab as X,B as g,l as m,ac as se}from"./index.433da608.js";const re={true:"inset",item:"item-inset","item-thumbnail":"item-thumbnail-inset"},$={xs:2,sm:4,md:8,lg:16,xl:24};var ge=T({name:"QSeparator",props:{...M,spaced:[Boolean,String],inset:[Boolean,String],vertical:Boolean,color:String,size:String},setup(e){const t=k(),l=W(e,t.proxy.$q),o=d(()=>e.vertical===!0?"vertical":"horizontal"),i=d(()=>` q-separator--${o.value}`),f=d(()=>e.inset!==!1?`${i.value}-${re[e.inset]}`:""),s=d(()=>`q-separator${i.value}${f.value}`+(e.color!==void 0?` bg-${e.color}`:"")+(l.value===!0?" q-separator--dark":"")),u=d(()=>{const c={};if(e.size!==void 0&&(c[e.vertical===!0?"width":"height"]=e.size),e.spaced!==!1){const b=e.spaced===!0?`${$.md}px`:e.spaced in $?`${$[e.spaced]}px`:e.spaced,r=e.vertical===!0?["Left","Right"]:["Top","Bottom"];c[`margin${r[0]}`]=c[`margin${r[1]}`]=b}return c});return()=>p("hr",{class:s.value,style:u.value,"aria-orientation":o.value})}}),pe=T({name:"QList",props:{...M,bordered:Boolean,dense:Boolean,separator:Boolean,padding:Boolean,tag:{type:String,default:"div"}},setup(e,{slots:t}){const l=k(),o=W(e,l.proxy.$q),i=d(()=>"q-list"+(e.bordered===!0?" q-list--bordered":"")+(e.dense===!0?" q-list--dense":"")+(e.separator===!0?" q-list--separator":"")+(o.value===!0?" q-list--dark":"")+(e.padding===!0?" q-list--padding":""));return()=>p(e.tag,{class:i.value},z(t.default))}});const ue=[null,document,document.body,document.scrollingElement,document.documentElement];function ye(e,t){let l=G(t);if(l===void 0){if(e==null)return window;l=e.closest(".scroll,.scroll-y,.overflow-auto")}return ue.includes(l)?window:l}function ce(e){return e===window?window.pageYOffset||window.scrollY||document.body.scrollTop||0:e.scrollTop}function de(e){return e===window?window.pageXOffset||window.scrollX||document.body.scrollLeft||0:e.scrollLeft}let C;function qe(){if(C!==void 0)return C;const e=document.createElement("p"),t=document.createElement("div");R(e,{width:"100%",height:"200px"}),R(t,{position:"absolute",top:"0px",left:"0px",visibility:"hidden",width:"200px",height:"150px",overflow:"hidden"}),t.appendChild(e),document.body.appendChild(t);const l=e.offsetWidth;t.style.overflow="scroll";let o=e.offsetWidth;return l===o&&(o=t.clientWidth),t.remove(),C=l-o,C}function fe(e,t=!0){return!e||e.nodeType!==Node.ELEMENT_NODE?!1:t?e.scrollHeight>e.clientHeight&&(e.classList.contains("scroll")||e.classList.contains("overflow-auto")||["auto","scroll"].includes(window.getComputedStyle(e)["overflow-y"])):e.scrollWidth>e.clientWidth&&(e.classList.contains("scroll")||e.classList.contains("overflow-auto")||["auto","scroll"].includes(window.getComputedStyle(e)["overflow-x"]))}var Le=T({name:"QItem",props:{...M,...J,tag:{type:String,default:"div"},active:{type:Boolean,default:null},clickable:Boolean,dense:Boolean,insetLevel:Number,tabindex:[String,Number],focused:Boolean,manualFocus:Boolean},emits:["click","keyup"],setup(e,{slots:t,emit:l}){const{proxy:{$q:o}}=k(),i=W(e,o),{hasLink:f,linkAttrs:s,linkClass:u,linkTag:c,navigateOnClick:b}=Z(),r=A(null),h=A(null),y=d(()=>e.clickable===!0||f.value===!0||e.tag==="label"),v=d(()=>e.disable!==!0&&y.value===!0),q=d(()=>"q-item q-item-type row no-wrap"+(e.dense===!0?" q-item--dense":"")+(i.value===!0?" q-item--dark":"")+(f.value===!0&&e.active===null?u.value:e.active===!0?` q-item--active${e.activeClass!==void 0?` ${e.activeClass}`:""}`:"")+(e.disable===!0?" disabled":"")+(v.value===!0?" q-item--clickable q-link cursor-pointer "+(e.manualFocus===!0?"q-manual-focusable":"q-focusable q-hoverable")+(e.focused===!0?" q-manual-focusable--focused":""):"")),x=d(()=>{if(e.insetLevel===void 0)return null;const a=o.lang.rtl===!0?"Right":"Left";return{["padding"+a]:16+e.insetLevel*56+"px"}});function E(a){v.value===!0&&(h.value!==null&&(a.qKeyEvent!==!0&&document.activeElement===r.value?h.value.focus():document.activeElement===h.value&&r.value.focus()),b(a))}function B(a){if(v.value===!0&&ee(a,[13,32])===!0){j(a),a.qKeyEvent=!0;const Q=new MouseEvent("click",a);Q.qKeyEvent=!0,r.value.dispatchEvent(Q)}l("keyup",a)}function n(){const a=te(t.default,[]);return v.value===!0&&a.unshift(p("div",{class:"q-focus-helper",tabindex:-1,ref:h})),a}return()=>{const a={ref:r,class:q.value,style:x.value,role:"listitem",onClick:E,onKeyup:B};return v.value===!0?(a.tabindex=e.tabindex||"0",Object.assign(a,s.value)):y.value===!0&&(a["aria-disabled"]="true"),p(c.value,a,n())}}}),Se=T({name:"QItemSection",props:{avatar:Boolean,thumbnail:Boolean,side:Boolean,top:Boolean,noWrap:Boolean},setup(e,{slots:t}){const l=d(()=>`q-item__section column q-item__section--${e.avatar===!0||e.side===!0||e.thumbnail===!0?"side":"main"}`+(e.top===!0?" q-item__section--top justify-start":" justify-center")+(e.avatar===!0?" q-item__section--avatar":"")+(e.thumbnail===!0?" q-item__section--thumbnail":"")+(e.noWrap===!0?" q-item__section--nowrap":""));return()=>p("div",{class:l.value},z(t.default))}}),Te=T({name:"QItemLabel",props:{overline:Boolean,caption:Boolean,header:Boolean,lines:[Number,String]},setup(e,{slots:t}){const l=d(()=>parseInt(e.lines,10)),o=d(()=>"q-item__label"+(e.overline===!0?" q-item__label--overline text-overline":"")+(e.caption===!0?" q-item__label--caption text-caption":"")+(e.header===!0?" q-item__label--header":"")+(l.value===1?" ellipsis":"")),i=d(()=>e.lines!==void 0&&l.value>1?{overflow:"hidden",display:"-webkit-box","-webkit-box-orient":"vertical","-webkit-line-clamp":l.value}:null);return()=>p("div",{style:i.value,class:o.value},z(t.default))}});function ke(){if(window.getSelection!==void 0){const e=window.getSelection();e.empty!==void 0?e.empty():e.removeAllRanges!==void 0&&(e.removeAllRanges(),le.is.mobile!==!0&&e.addRange(document.createRange()))}else document.selection!==void 0&&document.selection.empty()}const xe={modelValue:{type:Boolean,default:null},"onUpdate:modelValue":[Function,Array]},Ee=["beforeShow","show","beforeHide","hide"];function Be({showing:e,canShow:t,hideOnRouteChange:l,handleShow:o,handleHide:i,processOnMount:f}){const s=k(),{props:u,emit:c,proxy:b}=s;let r;function h(n){e.value===!0?q(n):y(n)}function y(n){if(u.disable===!0||n!==void 0&&n.qAnchorHandled===!0||t!==void 0&&t(n)!==!0)return;const a=u["onUpdate:modelValue"]!==void 0;a===!0&&(c("update:modelValue",!0),r=n,D(()=>{r===n&&(r=void 0)})),(u.modelValue===null||a===!1)&&v(n)}function v(n){e.value!==!0&&(e.value=!0,c("beforeShow",n),o!==void 0?o(n):c("show",n))}function q(n){if(u.disable===!0)return;const a=u["onUpdate:modelValue"]!==void 0;a===!0&&(c("update:modelValue",!1),r=n,D(()=>{r===n&&(r=void 0)})),(u.modelValue===null||a===!1)&&x(n)}function x(n){e.value!==!1&&(e.value=!1,c("beforeHide",n),i!==void 0?i(n):c("hide",n))}function E(n){u.disable===!0&&n===!0?u["onUpdate:modelValue"]!==void 0&&c("update:modelValue",!1):n===!0!==e.value&&(n===!0?v:x)(r)}I(()=>u.modelValue,E),l!==void 0&&oe(s)===!0&&I(()=>b.$route.fullPath,()=>{l.value===!0&&e.value===!0&&q()}),f===!0&&ie(()=>{E(u.modelValue)});const B={show:y,hide:q,toggle:h};return Object.assign(b,B),B}function Ce(){let e=null;const t=k();function l(){e!==null&&(clearTimeout(e),e=null)}return ne(l),F(l),{removeTimeout:l,registerTimeout(o,i){l(),ae(t)===!1&&(e=setTimeout(o,i))}}}function _e(e,t,l){let o;function i(){o!==void 0&&(X.remove(o),o=void 0)}return F(()=>{e.value===!0&&i()}),{removeFromHistory:i,addToHistory(){o={condition:()=>l.value===!0,handler:t},X.add(o)}}}let L=0,V,H,S,P=!1,Y,K,U,w=null;function ve(e){me(e)&&j(e)}function me(e){if(e.target===document.body||e.target.classList.contains("q-layout__backdrop"))return!0;const t=se(e),l=e.shiftKey&&!e.deltaX,o=!l&&Math.abs(e.deltaX)<=Math.abs(e.deltaY),i=l||o?e.deltaY:e.deltaX;for(let f=0;f<t.length;f++){const s=t[f];if(fe(s,o))return o?i<0&&s.scrollTop===0?!0:i>0&&s.scrollTop+s.clientHeight===s.scrollHeight:i<0&&s.scrollLeft===0?!0:i>0&&s.scrollLeft+s.clientWidth===s.scrollWidth}return!0}function N(e){e.target===document&&(document.scrollingElement.scrollTop=document.scrollingElement.scrollTop)}function _(e){P!==!0&&(P=!0,requestAnimationFrame(()=>{P=!1;const{height:t}=e.target,{clientHeight:l,scrollTop:o}=document.scrollingElement;(S===void 0||t!==window.innerHeight)&&(S=l-t,document.scrollingElement.scrollTop=o),o>S&&(document.scrollingElement.scrollTop-=Math.ceil((o-S)/8))}))}function O(e){const t=document.body,l=window.visualViewport!==void 0;if(e==="add"){const{overflowY:o,overflowX:i}=window.getComputedStyle(t);V=de(window),H=ce(window),Y=t.style.left,K=t.style.top,U=window.location.href,t.style.left=`-${V}px`,t.style.top=`-${H}px`,i!=="hidden"&&(i==="scroll"||t.scrollWidth>window.innerWidth)&&t.classList.add("q-body--force-scrollbar-x"),o!=="hidden"&&(o==="scroll"||t.scrollHeight>window.innerHeight)&&t.classList.add("q-body--force-scrollbar-y"),t.classList.add("q-body--prevent-scroll"),document.qScrollPrevented=!0,g.is.ios===!0&&(l===!0?(window.scrollTo(0,0),window.visualViewport.addEventListener("resize",_,m.passiveCapture),window.visualViewport.addEventListener("scroll",_,m.passiveCapture),window.scrollTo(0,0)):window.addEventListener("scroll",N,m.passiveCapture))}g.is.desktop===!0&&g.is.mac===!0&&window[`${e}EventListener`]("wheel",ve,m.notPassive),e==="remove"&&(g.is.ios===!0&&(l===!0?(window.visualViewport.removeEventListener("resize",_,m.passiveCapture),window.visualViewport.removeEventListener("scroll",_,m.passiveCapture)):window.removeEventListener("scroll",N,m.passiveCapture)),t.classList.remove("q-body--prevent-scroll"),t.classList.remove("q-body--force-scrollbar-x"),t.classList.remove("q-body--force-scrollbar-y"),document.qScrollPrevented=!1,t.style.left=Y,t.style.top=K,window.location.href===U&&window.scrollTo(V,H),S=void 0)}function we(e){let t="add";if(e===!0){if(L++,w!==null){clearTimeout(w),w=null;return}if(L>1)return}else{if(L===0||(L--,L>0))return;if(t="remove",g.is.ios===!0&&g.is.nativeMobile===!0){w!==null&&clearTimeout(w),w=setTimeout(()=>{O(t),w=null},100);return}}O(t)}function $e(){let e;return{preventBodyScroll(t){t!==e&&(e!==void 0||t===!0)&&(e=t,we(t))}}}function Ve(e,t,l){return l<=t?t:Math.min(l,Math.max(t,e))}function He(e,t,l){if(l<=t)return t;const o=l-t+1;let i=t+(e-t)%o;return i<t&&(i=o+i),i===0?0:i}export{Le as Q,ce as a,de as b,qe as c,ke as d,Ee as e,Ce as f,ye as g,Be as h,_e as i,$e as j,Ve as k,Se as l,Te as m,pe as n,ge as o,He as p,xe as u};