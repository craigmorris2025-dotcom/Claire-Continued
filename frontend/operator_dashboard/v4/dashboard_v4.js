(async function(){
  const target=document.getElementById("dashboard-v4-status");
  try{
    const response=await fetch("/api/dashboard/v4/payload",{cache:"no-store"});
    const payload=await response.json();
    if(target) target.textContent=`Completion ${payload.completion_percent || 0}%`;
  }catch(error){
    if(target) target.textContent="Dashboard V4 payload unavailable";
  }
})();
