const questions = [
  ["python","Python programming"],["java","Java programming"],["web","Web development"],
  ["maths","Mathematics & logical thinking"],["problem_solving","Problem-solving"],
  ["creativity","Creativity"],["communication","Communication"],
  ["data_interest","Interest in data & analysis"],["ai_interest","Interest in AI & automation"],
  ["security_interest","Interest in cybersecurity"],["design_interest","Interest in design & user experience"]
];
const ratings = document.getElementById("ratings");
questions.forEach(([key,label])=>{
  const wrap=document.createElement("div");wrap.className="rating-item";
  wrap.innerHTML=`<label for="${key}">${label}<output id="${key}_out">3</output></label><input id="${key}" name="${key}" type="range" min="0" max="5" value="3" step="1">`;
  ratings.appendChild(wrap);
  wrap.querySelector("input").addEventListener("input",e=>document.getElementById(key+"_out").textContent=e.target.value);
});
document.getElementById("careerForm").addEventListener("submit",async e=>{
  e.preventDefault();
  const btn=e.currentTarget.querySelector("button");btn.disabled=true;btn.textContent="Analyzing your profile...";
  const payload={student_name:document.getElementById("student_name").value.trim(),education:document.getElementById("education").value};
  questions.forEach(([key])=>payload[key]=Number(document.getElementById(key).value));
  try{
    const response=await fetch("/recommend",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    if(!response.ok)throw new Error("Could not generate recommendations");
    const data=await response.json();renderResults(data);
    document.getElementById("results").classList.remove("hidden");
    document.getElementById("results").scrollIntoView({behavior:"smooth"});
  }catch(err){alert("Something went wrong. Please make sure the Flask server is running and try again.");}
  finally{btn.disabled=false;btn.innerHTML='Generate my career matches <span>✦</span>';}
});
function renderResults(data){
  document.getElementById("resultTitle").textContent=`${data.student}, here are your career matches`;
  document.getElementById("resultSubtitle").textContent=`Education: ${data.education} · Explore these options as starting points`;
  document.getElementById("resultNote").textContent=data.note;
  const host=document.getElementById("careerResults");host.innerHTML="";
  data.results.forEach((r,i)=>{
    const card=document.createElement("article");card.className="career-card"+(i===0?" best":"");
    const skills=r.skills.map(s=>`<span class="chip">${escapeHtml(s)}</span>`).join("");
    const gaps=r.gaps.map(s=>`<span class="chip">${escapeHtml(s)}</span>`).join("");
    const roadmap=r.roadmap.map(s=>`<li>${escapeHtml(s)}</li>`).join("");
    card.innerHTML=`<span class="card-label">${i===0?"TOP MATCH":"CAREER OPTION "+String(i+1).padStart(2,"0")}</span>
      <h3>${escapeHtml(r.career)}</h3><p>${escapeHtml(r.description)}</p>
      <div class="match-row"><span>Profile compatibility indicator</span><strong>${r.score}%</strong></div>
      <div class="bar"><span style="width:${Math.min(100,r.score)}%"></span></div>
      <div class="detail-label">SKILLS TO DEVELOP</div><div class="chips">${skills}</div>
      <div class="detail-label">POSSIBLE SKILL GAPS TO WORK ON</div><div class="chips">${gaps}</div>
      <div class="detail-label">YOUR LEARNING ROADMAP</div><ul>${roadmap}</ul>`;
    host.appendChild(card);
  });
}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
