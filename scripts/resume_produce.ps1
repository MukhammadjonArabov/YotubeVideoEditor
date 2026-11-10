param([int]$ProjectId = 19, [string]$Quality = "final")
# Restarts the app + worker with the current code, then queues the whole production (images, voice, render) for one project.
# Used after the free Cloudflare image quota resets (05:00 Tashkent time). Output goes to tmp\resume_produce.log.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$py = Join-Path $root "venv\Scripts\python.exe"
$log = Join-Path $root "tmp\resume_produce.log"
New-Item -ItemType Directory -Force (Split-Path $log) | Out-Null
"$(Get-Date -Format s) resume project $ProjectId" | Out-File $log -Encoding utf8 -Append

Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'YotubeVideo' -or $_.CommandLine -match 'spawn_main' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 3
$env:PYTHONIOENCODING = "utf-8"
Start-Process -FilePath $py -ArgumentList "manage.py", "dev" -WorkingDirectory $root -WindowStyle Minimized `
    -RedirectStandardOutput (Join-Path $root "tmp\dev.out.log") -RedirectStandardError (Join-Path $root "tmp\dev.err.log")
Start-Sleep 25

$code = "from apps.videos.models import Project; from apps.videos import tasks; " +
        "p=Project.objects.get(pk=$ProjectId); " +
        "p.set_status(Project.Status.APPROVED, 'Avto-davom: rasm limiti yangilandi.'); " +
        "Project.objects.filter(pk=$ProjectId).update(progress_message='Navbatda...'); " +
        "tasks.enqueue('produce_video', p, '$Quality', False); print('queued')"
& $py manage.py shell -c $code 2>&1 | Out-File $log -Encoding utf8 -Append
