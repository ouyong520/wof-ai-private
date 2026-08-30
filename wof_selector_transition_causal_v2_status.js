(()=>{
'use strict';
const running=!!self.__WOF_SELECTOR_TRANSITION_V2_RUNNING;
const result=self.__WOF_SELECTOR_TRANSITION_CAUSAL_V2||null;
const out={version:'wof-selector-transition-causal-v2-status-v1',running,hasResult:!!result,casesCaptured:result?.casesCaptured??null,result};
console.log('=== SELECTOR TRANSITION CAUSAL V2 STATUS ===');
console.log(JSON.stringify(out,null,2));
return out;
})();
