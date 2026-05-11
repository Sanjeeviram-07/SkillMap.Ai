from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google", response_class=HTMLResponse)
async def google_auth_page():
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8501')
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-app-compat.js"></script>
        <script src="https://www.gstatic.com/firebasejs/10.8.0/firebase-auth-compat.js"></script>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
                background: transparent;
            }
            .google-btn {
                background-color: white;
                color: #2C2C2C;
                font-family: 'Inter', sans-serif;
                font-weight: 600;
                font-size: 0.95rem;
                padding: 11px;
                border: 1.5px solid #CBCBCB;
                border-radius: 10px;
                width: 100%;
                height: 100%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                transition: all 0.2s ease;
                box-sizing: border-box;
            }
            .google-btn:hover {
                background-color: #f8f9fa;
                border-color: #6D8196;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            }
            .google-btn img {
                width: 20px;
                height: 20px;
            }
        </style>
    </head>
    <body>
        <button class="google-btn" id="googleSignInBtn" type="button">
            <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google Logo">
            Continue with Google
        </button>
        <script>
            var firebaseConfig = {
                apiKey: "AIzaSyDwIDERP4WzAYrmBvdtx6_xwvwLxiKh-KY",
                authDomain: "skillmap-ai-4bf7e.firebaseapp.com",
                projectId: "skillmap-ai-4bf7e",
                storageBucket: "skillmap-ai-4bf7e.firebasestorage.app",
                messagingSenderId: "33095485416",
                appId: "1:33095485416:web:10af6946c8a6057f13865d",
                measurementId: "G-VQ9CN3B5KX"
            };

            if (!firebase.apps.length) {
                firebase.initializeApp(firebaseConfig);
            }

            document.getElementById("googleSignInBtn").addEventListener("click", function() {
                var provider = new firebase.auth.GoogleAuthProvider();
                firebase.auth().signInWithPopup(provider)
                .then(function(result) {
                    var user = result.user;
                    var parentUrl;
                    try {
                        parentUrl = new URL(document.referrer);
                    } catch(e) {
                        parentUrl = new URL("{{FRONTEND_URL}}");
                    }
                    parentUrl.searchParams.set("google_uid", user.uid);
                    parentUrl.searchParams.set("email", user.email);
                    parentUrl.searchParams.set("name", user.displayName);
                    window.top.location.href = parentUrl.toString();
                }).catch(function(error) {
                    console.error("Google Sign-In Error:", error);
                    alert("Google Sign-In Error: " + error.message);
                });
            });
        </script>
    </body>
    </html>
    """
    return html.replace("{{FRONTEND_URL}}", frontend_url)
