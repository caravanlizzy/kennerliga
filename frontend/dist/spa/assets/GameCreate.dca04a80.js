import{u as se,f as ce,a as fe,g as de,c as me,b as ve,e as ne,h as X,i as ge}from"./use-key-composition.1dd9310f.js";import{r as U,w as D,f as Z,aw as he,a as j,c as le,e as ke,o as oe,h as Q,an as ye,g as ie,H as J,a9 as xe,ah as we,d as Me,aa as be,K as ee,q as Se,aF as Ce,m as Fe,aH as Ve,N as Ee,x as Re,y as Ae,a1 as re,z as W,O as Pe,Q as Te}from"./index.433da608.js";import"./use-dark.0291611e.js";const te={date:"####/##/##",datetime:"####/##/## ##:##",time:"##:##",fulltime:"##:##:##",phone:"(###) ### - ####",card:"#### #### #### ####"},G={"#":{pattern:"[\\d]",negate:"[^\\d]"},S:{pattern:"[a-zA-Z]",negate:"[^a-zA-Z]"},N:{pattern:"[0-9a-zA-Z]",negate:"[^0-9a-zA-Z]"},A:{pattern:"[a-zA-Z]",negate:"[^a-zA-Z]",transform:e=>e.toLocaleUpperCase()},a:{pattern:"[a-zA-Z]",negate:"[^a-zA-Z]",transform:e=>e.toLocaleLowerCase()},X:{pattern:"[0-9a-zA-Z]",negate:"[^0-9a-zA-Z]",transform:e=>e.toLocaleUpperCase()},x:{pattern:"[0-9a-zA-Z]",negate:"[^0-9a-zA-Z]",transform:e=>e.toLocaleLowerCase()}},ue=Object.keys(G);ue.forEach(e=>{G[e].regex=new RegExp(G[e].pattern)});const Oe=new RegExp("\\\\([^.*+?^${}()|([\\]])|([.*+?^${}()|[\\]])|(["+ue.join("")+"])|(.)","g"),ae=/[.*+?^${}()|[\]\\]/g,w=String.fromCharCode(1),_e={mask:String,reverseFillMask:Boolean,fillMask:[Boolean,String],unmaskedValue:Boolean};function qe(e,C,O,S){let u,s,g,T,I,k;const b=U(null),f=U(i());function $(){return e.autogrow===!0||["textarea","text","search","url","tel","password"].includes(e.type)}D(()=>e.type+e.autogrow,_),D(()=>e.mask,l=>{if(l!==void 0)N(f.value,!0);else{const a=P(f.value);_(),e.modelValue!==a&&C("update:modelValue",a)}}),D(()=>e.fillMask+e.reverseFillMask,()=>{b.value===!0&&N(f.value,!0)}),D(()=>e.unmaskedValue,()=>{b.value===!0&&N(f.value)});function i(){if(_(),b.value===!0){const l=E(P(e.modelValue));return e.fillMask!==!1?Y(l):l}return e.modelValue}function F(l){if(l<u.length)return u.slice(-l);let a="",o=u;const n=o.indexOf(w);if(n>-1){for(let c=l-o.length;c>0;c--)a+=w;o=o.slice(0,n)+a+o.slice(n)}return o}function _(){if(b.value=e.mask!==void 0&&e.mask.length!==0&&$(),b.value===!1){T=void 0,u="",s="";return}const l=te[e.mask]===void 0?e.mask:te[e.mask],a=typeof e.fillMask=="string"&&e.fillMask.length!==0?e.fillMask.slice(0,1):"_",o=a.replace(ae,"\\$&"),n=[],c=[],r=[];let x=e.reverseFillMask===!0,d="",m="";l.replace(Oe,(M,t,h,p,B)=>{if(p!==void 0){const R=G[p];r.push(R),m=R.negate,x===!0&&(c.push("(?:"+m+"+)?("+R.pattern+"+)?(?:"+m+"+)?("+R.pattern+"+)?"),x=!1),c.push("(?:"+m+"+)?("+R.pattern+")?")}else if(h!==void 0)d="\\"+(h==="\\"?"":h),r.push(h),n.push("([^"+d+"]+)?"+d+"?");else{const R=t!==void 0?t:B;d=R==="\\"?"\\\\\\\\":R.replace(ae,"\\\\$&"),r.push(R),n.push("([^"+d+"]+)?"+d+"?")}});const z=new RegExp("^"+n.join("")+"("+(d===""?".":"[^"+d+"]")+"+)?"+(d===""?"":"["+d+"]*")+"$"),K=c.length-1,v=c.map((M,t)=>t===0&&e.reverseFillMask===!0?new RegExp("^"+o+"*"+M):t===K?new RegExp("^"+M+"("+(m===""?".":m)+"+)?"+(e.reverseFillMask===!0?"$":o+"*")):new RegExp("^"+M));g=r,T=M=>{const t=z.exec(e.reverseFillMask===!0?M:M.slice(0,r.length+1));t!==null&&(M=t.slice(1).join(""));const h=[],p=v.length;for(let B=0,R=M;B<p;B++){const H=v[B].exec(R);if(H===null)break;R=R.slice(H.shift().length),h.push(...H)}return h.length!==0?h.join(""):M},u=r.map(M=>typeof M=="string"?M:w).join(""),s=u.split(w).join(a)}function N(l,a,o){const n=S.value,c=n.selectionEnd,r=n.value.length-c,x=P(l);a===!0&&_();const d=E(x),m=e.fillMask!==!1?Y(d):d,z=f.value!==m;n.value!==m&&(n.value=m),z===!0&&(f.value=m),document.activeElement===n&&Z(()=>{if(m===s){const v=e.reverseFillMask===!0?s.length:0;n.setSelectionRange(v,v,"forward");return}if(o==="insertFromPaste"&&e.reverseFillMask!==!0){const v=n.selectionEnd;let M=c-1;for(let t=I;t<=M&&t<v;t++)u[t]!==w&&M++;A.right(n,M);return}if(["deleteContentBackward","deleteContentForward"].indexOf(o)>-1){const v=e.reverseFillMask===!0?c===0?m.length>d.length?1:0:Math.max(0,m.length-(m===s?0:Math.min(d.length,r)+1))+1:c;n.setSelectionRange(v,v,"forward");return}if(e.reverseFillMask===!0)if(z===!0){const v=Math.max(0,m.length-(m===s?0:Math.min(d.length,r+1)));v===1&&c===1?n.setSelectionRange(v,v,"forward"):A.rightReverse(n,v)}else{const v=m.length-r;n.setSelectionRange(v,v,"backward")}else if(z===!0){const v=Math.max(0,u.indexOf(w),Math.min(d.length,c)-1);A.right(n,v)}else{const v=c-1;A.right(n,v)}});const K=e.unmaskedValue===!0?P(m):m;String(e.modelValue)!==K&&(e.modelValue!==null||K!=="")&&O(K,!0)}function L(l,a,o){const n=E(P(l.value));a=Math.max(0,u.indexOf(w),Math.min(n.length,a)),I=a,l.setSelectionRange(a,o,"forward")}const A={left(l,a){const o=u.slice(a-1).indexOf(w)===-1;let n=Math.max(0,a-1);for(;n>=0;n--)if(u[n]===w){a=n,o===!0&&a++;break}if(n<0&&u[a]!==void 0&&u[a]!==w)return A.right(l,0);a>=0&&l.setSelectionRange(a,a,"backward")},right(l,a){const o=l.value.length;let n=Math.min(o,a+1);for(;n<=o;n++)if(u[n]===w){a=n;break}else u[n-1]===w&&(a=n);if(n>o&&u[a-1]!==void 0&&u[a-1]!==w)return A.left(l,o);l.setSelectionRange(a,a,"forward")},leftReverse(l,a){const o=F(l.value.length);let n=Math.max(0,a-1);for(;n>=0;n--)if(o[n-1]===w){a=n;break}else if(o[n]===w&&(a=n,n===0))break;if(n<0&&o[a]!==void 0&&o[a]!==w)return A.rightReverse(l,0);a>=0&&l.setSelectionRange(a,a,"backward")},rightReverse(l,a){const o=l.value.length,n=F(o),c=n.slice(0,a+1).indexOf(w)===-1;let r=Math.min(o,a+1);for(;r<=o;r++)if(n[r-1]===w){a=r,a>0&&c===!0&&a--;break}if(r>o&&n[a-1]!==void 0&&n[a-1]!==w)return A.leftReverse(l,o);l.setSelectionRange(a,a,"forward")}};function y(l){C("click",l),k=void 0}function V(l){if(C("keydown",l),he(l)===!0||l.altKey===!0)return;const a=S.value,o=a.selectionStart,n=a.selectionEnd;if(l.shiftKey||(k=void 0),l.keyCode===37||l.keyCode===39){l.shiftKey&&k===void 0&&(k=a.selectionDirection==="forward"?o:n);const c=A[(l.keyCode===39?"right":"left")+(e.reverseFillMask===!0?"Reverse":"")];if(l.preventDefault(),c(a,k===o?n:o),l.shiftKey){const r=a.selectionStart;a.setSelectionRange(Math.min(k,r),Math.max(k,r),"forward")}}else l.keyCode===8&&e.reverseFillMask!==!0&&o===n?(A.left(a,o),a.setSelectionRange(a.selectionStart,n,"backward")):l.keyCode===46&&e.reverseFillMask===!0&&o===n&&(A.rightReverse(a,n),a.setSelectionRange(o,a.selectionEnd,"forward"))}function E(l){if(l==null||l==="")return"";if(e.reverseFillMask===!0)return q(l);const a=g;let o=0,n="";for(let c=0;c<a.length;c++){const r=l[o],x=a[c];if(typeof x=="string")n+=x,r===x&&o++;else if(r!==void 0&&x.regex.test(r))n+=x.transform!==void 0?x.transform(r):r,o++;else return n}return n}function q(l){const a=g,o=u.indexOf(w);let n=l.length-1,c="";for(let r=a.length-1;r>=0&&n>-1;r--){const x=a[r];let d=l[n];if(typeof x=="string")c=x+c,d===x&&n--;else if(d!==void 0&&x.regex.test(d))do c=(x.transform!==void 0?x.transform(d):d)+c,n--,d=l[n];while(o===r&&d!==void 0&&x.regex.test(d));else return c}return c}function P(l){return typeof l!="string"||T===void 0?typeof l=="number"?T(""+l):l:T(l)}function Y(l){return s.length-l.length<=0?l:e.reverseFillMask===!0&&l.length!==0?s.slice(0,-l.length)+l:l+s.slice(l.length)}return{innerValue:f,hasMask:b,moveCursorForPaste:L,updateMaskValue:N,onMaskedKeydown:V,onMaskedClick:y}}function Be(e,C){function O(){const S=e.modelValue;try{const u="DataTransfer"in window?new DataTransfer:"ClipboardEvent"in window?new ClipboardEvent("").clipboardData:void 0;return Object(S)===S&&("length"in S?Array.from(S):[S]).forEach(s=>{u.items.add(s)}),{files:u.files}}catch{return{files:void 0}}}return C===!0?j(()=>{if(e.type==="file")return O()}):j(O)}var Ie=le({name:"QInput",inheritAttrs:!1,props:{...se,..._e,...ce,modelValue:{required:!1},shadowText:String,type:{type:String,default:"text"},debounce:[String,Number],autogrow:Boolean,inputClass:[Array,String,Object],inputStyle:[Array,String,Object]},emits:[...fe,"paste","change","keydown","click","animationend"],setup(e,{emit:C,attrs:O}){const{proxy:S}=ie(),{$q:u}=S,s={};let g=NaN,T,I,k=null,b;const f=U(null),$=de(e),{innerValue:i,hasMask:F,moveCursorForPaste:_,updateMaskValue:N,onMaskedKeydown:L,onMaskedClick:A}=qe(e,C,d,f),y=Be(e,!0),V=j(()=>X(i.value)),E=ge(r),q=me(),P=j(()=>e.type==="textarea"||e.autogrow===!0),Y=j(()=>P.value===!0||["text","search","url","tel","password"].includes(e.type)),l=j(()=>{const t={...q.splitAttrs.listeners.value,onInput:r,onPaste:c,onChange:z,onBlur:K,onFocus:J};return t.onCompositionstart=t.onCompositionupdate=t.onCompositionend=E,F.value===!0&&(t.onKeydown=L,t.onClick=A),e.autogrow===!0&&(t.onAnimationend=x),t}),a=j(()=>{const t={tabindex:0,"data-autofocus":e.autofocus===!0||void 0,rows:e.type==="textarea"?6:void 0,"aria-label":e.label,name:$.value,...q.splitAttrs.attributes.value,id:q.targetUid.value,maxlength:e.maxlength,disabled:e.disable===!0,readonly:e.readonly===!0};return P.value===!1&&(t.type=e.type),e.autogrow===!0&&(t.rows=1),t});D(()=>e.type,()=>{f.value&&(f.value.value=e.modelValue)}),D(()=>e.modelValue,t=>{if(F.value===!0){if(I===!0&&(I=!1,String(t)===g))return;N(t)}else i.value!==t&&(i.value=t,e.type==="number"&&s.hasOwnProperty("value")===!0&&(T===!0?T=!1:delete s.value));e.autogrow===!0&&Z(m)}),D(()=>e.autogrow,t=>{t===!0?Z(m):f.value!==null&&O.rows>0&&(f.value.style.height="auto")}),D(()=>e.dense,()=>{e.autogrow===!0&&Z(m)});function o(){ne(()=>{const t=document.activeElement;f.value!==null&&f.value!==t&&(t===null||t.id!==q.targetUid.value)&&f.value.focus({preventScroll:!0})})}function n(){f.value!==null&&f.value.select()}function c(t){if(F.value===!0&&e.reverseFillMask!==!0){const h=t.target;_(h,h.selectionStart,h.selectionEnd)}C("paste",t)}function r(t){if(!t||!t.target)return;if(e.type==="file"){C("update:modelValue",t.target.files);return}const h=t.target.value;if(t.target.qComposing===!0){s.value=h;return}if(F.value===!0)N(h,!1,t.inputType);else if(d(h),Y.value===!0&&t.target===document.activeElement){const{selectionStart:p,selectionEnd:B}=t.target;p!==void 0&&B!==void 0&&Z(()=>{t.target===document.activeElement&&h.indexOf(t.target.value)===0&&t.target.setSelectionRange(p,B)})}e.autogrow===!0&&m()}function x(t){C("animationend",t),m()}function d(t,h){b=()=>{k=null,e.type!=="number"&&s.hasOwnProperty("value")===!0&&delete s.value,e.modelValue!==t&&g!==t&&(g=t,h===!0&&(I=!0),C("update:modelValue",t),Z(()=>{g===t&&(g=NaN)})),b=void 0},e.type==="number"&&(T=!0,s.value=t),e.debounce!==void 0?(k!==null&&clearTimeout(k),s.value=t,k=setTimeout(b,e.debounce)):b()}function m(){requestAnimationFrame(()=>{const t=f.value;if(t!==null){const h=t.parentNode.style,{scrollTop:p}=t,{overflowY:B,maxHeight:R}=u.platform.is.firefox===!0?{}:window.getComputedStyle(t),H=B!==void 0&&B!=="scroll";H===!0&&(t.style.overflowY="hidden"),h.marginBottom=t.scrollHeight-1+"px",t.style.height="1px",t.style.height=t.scrollHeight+"px",H===!0&&(t.style.overflowY=parseInt(R,10)<t.scrollHeight?"auto":"hidden"),h.marginBottom="",t.scrollTop=p}})}function z(t){E(t),k!==null&&(clearTimeout(k),k=null),b!==void 0&&b(),C("change",t.target.value)}function K(t){t!==void 0&&J(t),k!==null&&(clearTimeout(k),k=null),b!==void 0&&b(),T=!1,I=!1,delete s.value,e.type!=="file"&&setTimeout(()=>{f.value!==null&&(f.value.value=i.value!==void 0?i.value:"")})}function v(){return s.hasOwnProperty("value")===!0?s.value:i.value!==void 0?i.value:""}ke(()=>{K()}),oe(()=>{e.autogrow===!0&&m()}),Object.assign(q,{innerValue:i,fieldClass:j(()=>`q-${P.value===!0?"textarea":"input"}`+(e.autogrow===!0?" q-textarea--autogrow":"")),hasShadow:j(()=>e.type!=="file"&&typeof e.shadowText=="string"&&e.shadowText.length!==0),inputRef:f,emitValue:d,hasValue:V,floatingLabel:j(()=>V.value===!0&&(e.type!=="number"||isNaN(i.value)===!1)||X(e.displayValue)),getControl:()=>Q(P.value===!0?"textarea":"input",{ref:f,class:["q-field__native q-placeholder",e.inputClass],style:e.inputStyle,...a.value,...l.value,...e.type!=="file"?{value:v()}:y.value}),getShadowControl:()=>Q("div",{class:"q-field__native q-field__shadow absolute-bottom no-pointer-events"+(P.value===!0?"":" text-no-wrap")},[Q("span",{class:"invisible"},v()),Q("span",e.shadowText)])});const M=ve(q);return Object.assign(S,{focus:o,select:n,getNativeElement:()=>f.value}),ye(S,"nativeEl",()=>f.value),M}}),Ne=le({name:"QForm",props:{autofocus:Boolean,noErrorFocus:Boolean,noResetFocus:Boolean,greedy:Boolean,onSubmit:Function},emits:["reset","validationSuccess","validationError"],setup(e,{slots:C,emit:O}){const S=ie(),u=U(null);let s=0;const g=[];function T(i){const F=typeof i=="boolean"?i:e.noErrorFocus!==!0,_=++s,N=(y,V)=>{O("validation"+(y===!0?"Success":"Error"),V)},L=y=>{const V=y.validate();return typeof V.then=="function"?V.then(E=>({valid:E,comp:y}),E=>({valid:!1,comp:y,err:E})):Promise.resolve({valid:V,comp:y})};return(e.greedy===!0?Promise.all(g.map(L)).then(y=>y.filter(V=>V.valid!==!0)):g.reduce((y,V)=>y.then(()=>L(V).then(E=>{if(E.valid===!1)return Promise.reject(E)})),Promise.resolve()).catch(y=>[y])).then(y=>{if(y===void 0||y.length===0)return _===s&&N(!0),!0;if(_===s){const{comp:V,err:E}=y[0];if(E!==void 0&&console.error(E),N(!1,V),F===!0){const q=y.find(({comp:P})=>typeof P.focus=="function"&&be(P.$)===!1);q!==void 0&&q.comp.focus()}}return!1})}function I(){s++,g.forEach(i=>{typeof i.resetValidation=="function"&&i.resetValidation()})}function k(i){i!==void 0&&ee(i);const F=s+1;T().then(_=>{F===s&&_===!0&&(e.onSubmit!==void 0?O("submit",i):i!==void 0&&i.target!==void 0&&typeof i.target.submit=="function"&&i.target.submit())})}function b(i){i!==void 0&&ee(i),O("reset"),Z(()=>{I(),e.autofocus===!0&&e.noResetFocus!==!0&&f()})}function f(){ne(()=>{if(u.value===null)return;const i=u.value.querySelector("[autofocus][tabindex], [data-autofocus][tabindex]")||u.value.querySelector("[autofocus] [tabindex], [data-autofocus] [tabindex]")||u.value.querySelector("[autofocus], [data-autofocus]")||Array.prototype.find.call(u.value.querySelectorAll("[tabindex]"),F=>F.tabIndex>-1);i!=null&&i.focus({preventScroll:!0})})}Se(Ce,{bindComponent(i){g.push(i)},unbindComponent(i){const F=g.indexOf(i);F>-1&&g.splice(F,1)}});let $=!1;return xe(()=>{$=!0}),we(()=>{$===!0&&e.autofocus===!0&&f()}),oe(()=>{e.autofocus===!0&&f()}),Object.assign(S.proxy,{validate:T,resetValidation:I,submit:k,reset:b,focus:f,getValidationComponents:()=>g}),()=>Q("form",{class:"q-form",ref:u,onSubmit:k,onReset:b},Me(C.default))}});function je(){return Fe(Ve)}const pe={class:"q-pa-md bg-primary text-white"},Ke=re("p",{class:"text-h5"},"Neues Spiel",-1),De={class:"q-py-md",style:{"max-width":"400px"}},Le=Ee({__name:"GameCreate",setup(e){const C=je(),O=()=>{console.log("test"),C.notify({color:"positive",textColor:"white",icon:"save",message:"Gespeichert"})},S=U("");return(u,s)=>(Re(),Ae("div",pe,[Ke,re("div",De,[W(Ne,{onSubmit:O,class:"q-gutter-md"},{default:Pe(()=>[W(Ie,{dark:"",color:"white","label-color":"info",filled:"",modelValue:S.value,"onUpdate:modelValue":s[0]||(s[0]=g=>S.value=g),label:"Spielname","lazy-rules":"",rules:[g=>g.length>0&&g!==null||"Spielname ist Pflicht"]},null,8,["modelValue","rules"]),W(Te,{type:"submit",color:"positive",label:"Speichern"})]),_:1})])]))}});export{Le as default};