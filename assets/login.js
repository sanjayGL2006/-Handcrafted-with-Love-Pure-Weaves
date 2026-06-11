// login.js — separated frontend logic for Pure Weaves login page
(function(){
  'use strict';

  // Utility: safe fetch with timeout
  function safeFetch(url, options, timeout=8000){
    const controller = new AbortController();
    const sig = controller.signal;
    const timer = setTimeout(()=>controller.abort(), timeout);
    return fetch(url, Object.assign({}, options||{}, {signal: sig}))
      .finally(()=>clearTimeout(timer));
  }

  // DOM helpers
  const $ = id => document.getElementById(id);

  // UI elements
  const googleBtn = $('googleBtn');
  const emailLoginBtn = $('emailLoginBtn');
  const emailRegisterBtn = $('emailRegisterBtn');
  const firebaseBadge = $('firebaseBadge');
  const googleError = $('googleError');
  const googleErrorText = $('googleErrorText');
  const emailError = $('emailError');
  const emailErrorText = $('emailErrorText');
  const successScreen = $('successScreen');
  const redirectFill = $('redirectFill');

  // Determine API base: for static file, default to same origin
  const API_BASE = (window.location.protocol === 'file:') ? 'http://127.0.0.1:5000' : window.location.origin;

  // Init firebase if present
  let firebaseReady = false;
  let auth = null;
  try{
    if (window.firebase && firebase.apps !== undefined){
      // Allow server-provided config in window.PW_FIREBASE_CONFIG
      const config = window.PW_FIREBASE_CONFIG || window.firebaseConfig || null;
      if (config) firebase.initializeApp(config);
      auth = firebase.auth();
      firebaseReady = true;
      firebaseBadge.className = 'firebase-badge';
      firebaseBadge.textContent = '✅ Firebase Connected — Secure Login Ready';
      setTimeout(()=>firebaseBadge.style.display='none', 3000);

      auth.onAuthStateChanged(user=>{
        if (!user) return;
        // Exchange firebase user for backend token (best effort)
        safeFetch('/api/auth/google', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({google_id:user.uid,email:user.email,name:user.displayName||''})})
          .then(r=>r.json().then(d=>({ok:r.ok,data:d}))).then(resp=>{
            if (resp.ok) saveAndLogin(resp.data.user, resp.data.token);
            else saveAndLogin({name:user.displayName||'Google User',email:user.email,id:user.uid,loginType:'google'}, null);
          }).catch(()=>saveAndLogin({name:user.displayName||'Google User',email:user.email,id:user.uid,loginType:'google'}, null));
      });
    }
  }catch(e){
    console.warn('Firebase init failed', e);
    firebaseBadge.className = 'firebase-badge error';
    firebaseBadge.textContent = '⚠️ Firebase not configured — Demo mode';
    setTimeout(()=>firebaseBadge.style.display='none',3000);
  }

  // Tab switching
  document.querySelectorAll('.tab-btn').forEach(btn=>btn.addEventListener('click', function(){
    document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    this.classList.add('active');
    const target = this.id === 'tab-google' ? 'panel-google' : 'panel-email';
    document.getElementById(target).classList.add('active');
  }));

  // Google sign-in
  function signInWithGoogle(){
    googleBtn.disabled = true;
    googleBtn.textContent = 'Connecting...';
    if (firebaseReady && auth){
      const provider = new firebase.auth.GoogleAuthProvider();
      provider.addScope('email');
      provider.addScope('profile');
      auth.signInWithPopup(provider).then(result=>{
        const user = result.user;
        safeFetch(API_BASE + '/api/auth/google', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({google_id:user.uid,email:user.email,name:user.displayName||''})})
          .then(r=>r.json().then(d=>({ok:r.ok,data:d}))).then(resp=>{
            googleBtn.disabled = false; googleBtn.textContent = 'Continue with Google';
            if (resp.ok) saveAndLogin(resp.data.user, resp.data.token);
            else saveAndLogin({name:user.displayName||'Google User',email:user.email,id:user.uid,loginType:'google'}, null);
          }).catch(err=>{
            googleBtn.disabled = false; googleBtn.textContent = 'Continue with Google';
            showGoogleError('Network error');
          });
      }).catch(err=>{
        googleBtn.disabled = false; googleBtn.textContent = 'Continue with Google';
        if (err && err.code === 'auth/unauthorized-domain') showGoogleError('Unauthorized domain for Firebase OAuth');
        else if (err && err.code !== 'auth/popup-closed-by-user') showGoogleError(err.message || 'Google login failed');
      });
    }else{
      // Demo fallback
      setTimeout(()=>saveAndLogin({name:'Google User',email:'demo@pureweaves.local',id:'demo_'+Date.now()}, null), 800);
    }
  }

  function showGoogleError(msg){
    googleError.style.display = 'block';
    googleErrorText.textContent = msg;
  }

  // Email login
  function loginWithEmail(){
    emailError.style.display = 'none';
    const email = $('emailInput').value.trim();
    const password = $('passwordInput').value || '';
    if (!email || !password){
      showEmailError('Please enter email and password');
      return;
    }
    emailLoginBtn.disabled = true; emailLoginBtn.textContent = 'Signing in...';
    safeFetch(API_BASE + '/api/auth/login', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})})
      .then(r=>r.json().then(d=>({ok:r.ok,data:d}))).then(resp=>{
        emailLoginBtn.disabled = false; emailLoginBtn.textContent = 'Login';
        if (resp.ok){
          saveAndLogin(resp.data.user, resp.data.token);
        }else{
          showEmailError((resp.data && resp.data.error) || 'Login failed');
        }
      }).catch(err=>{
        emailLoginBtn.disabled = false; emailLoginBtn.textContent = 'Login';
        showEmailError('Network error');
      });
  }

  function showEmailError(msg){
    emailError.style.display = 'block';
    emailErrorText.textContent = msg;
  }

  function saveAndLogin(user, token){
    try{
      let state = {};
      try{ state = JSON.parse(localStorage.getItem('pureweaves_state')||'{}'); }catch(e){ state = {} }
      state.user = user; if (token) state.token = token;
      if (!state.customers) state.customers = [];
      const exists = state.customers.find(c=>c.id===user.id || (c.mobile && c.mobile===user.mobile));
      if (!exists){ state.customers.unshift(Object.assign({}, user, {joined: new Date().toLocaleDateString('en-IN'), lastLogin: new Date().toLocaleString('en-IN')})); if (state.customers.length>200) state.customers = state.customers.slice(0,200); }
      localStorage.setItem('pureweaves_state', JSON.stringify(state));
    }catch(e){}
    // Show success and redirect
    document.getElementById('loginContent').style.display = 'none';
    successScreen.classList.add('show');
    redirectFill.style.width = '100%';
    setTimeout(()=>{
      try{ sessionStorage.setItem('pureweaves_just_logged_in','1'); }catch(e){}
      const origin = window.location.protocol.startsWith('http') ? window.location.origin : 'http://127.0.0.1:5000';
      window.location.href = origin + '/index.html';
    }, 1200);
  }

  // Event listeners
  if (googleBtn) googleBtn.addEventListener('click', signInWithGoogle);
  if (emailLoginBtn) emailLoginBtn.addEventListener('click', loginWithEmail);
  if (emailRegisterBtn) emailRegisterBtn.addEventListener('click', ()=>{ window.location.href = '/register.html'; });

  // Expose for debugging
  window.__PW = { loginWithEmail, signInWithGoogle };
})();
