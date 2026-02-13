@echo off
setlocal
echo ===================================================
echo   ReqGen Final Setup Assistant
echo ===================================================
echo.
echo Please deploy your backend to Koyeb using the button in README.md
echo or manually at https://app.koyeb.com/
echo.
echo Once deployed, copy the "Public App URL" from Koyeb.
echo.
set /p BACKEND_URL="Paste your Koyeb Backend URL here (e.g., https://app.koyeb.com): "

if "%BACKEND_URL%"=="" goto error

echo.
echo Updating vercel.json...
(
echo {
echo     "version": 2,
echo     "buildCommand": "npx vite build",
echo     "outputDirectory": "dist/public",
echo     "framework": "vite",
echo     "rewrites": [
echo         {
echo             "source": "/api/:path*",
echo             "destination": "%BACKEND_URL%/api/:path*"
echo         }
echo     ],
echo     "headers": [
echo         {
echo             "source": "/(.*)",
echo             "headers": [
echo                 {
echo                     "key": "X-Content-Type-Options",
echo                     "value": "nosniff"
echo                 }
echo             ]
echo         }
echo     ]
echo }
) > vercel.json

echo.
echo Pushing configuration to GitHub...
git add vercel.json
git commit -m "Linked Vercel to Backend URL: %BACKEND_URL%"
git push

echo.
echo ===================================================
echo   SUCCESS! 
echo   Your Vercel app will now redeploy automatically.
echo   Wait 2 minutes, then try Logging in.
echo ===================================================
pause
exit /b

:error
echo Error: URL cannot be empty.
pause
