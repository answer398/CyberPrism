# CyberPrism Docker镜像管理脚本 (PowerShell版本)
# 用于快速管理和查看CyberPrism平台的Docker镜像

# 显示帮助信息
function Show-Help {
    Write-Host "CyberPrism Docker镜像管理工具" -ForegroundColor Green
    Write-Host ""
    Write-Host "用法: .\manage-images.ps1 [命令] [选项]"
    Write-Host ""
    Write-Host "命令:"
    Write-Host "  list                    列出所有CyberPrism镜像"
    Write-Host "  list-web                列出所有Web类题目镜像"
    Write-Host "  list-pwn                列出所有Pwn类题目镜像"
    Write-Host "  list-easy               列出所有简单难度镜像"
    Write-Host "  list-medium             列出所有中等难度镜像"
    Write-Host "  list-hard               列出所有困难难度镜像"
    Write-Host "  info <镜像名>           显示镜像详细信息"
    Write-Host "  build <题目目录>        构建指定题目的镜像"
    Write-Host "  build-all               构建所有题目镜像"
    Write-Host "  clean-dangling          清理悬空镜像"
    Write-Host "  clean-unused            清理所有未使用的镜像"
    Write-Host "  clean-all               删除所有CyberPrism镜像"
    Write-Host "  stats                   显示镜像统计信息"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\manage-images.ps1 list"
    Write-Host "  .\manage-images.ps1 list-web"
    Write-Host "  .\manage-images.ps1 info cyberprism/web-easy:latest"
    Write-Host "  .\manage-images.ps1 build challenges\web-easy"
    Write-Host "  .\manage-images.ps1 build-all"
}

# 列出所有CyberPrism镜像
function List-All {
    Write-Host "=== 所有CyberPrism镜像 ===" -ForegroundColor Blue
    docker images --filter=reference='cyberprism/*' --format "table {{.Repository}}`t{{.Tag}}`t{{.Size}}`t{{.CreatedAt}}"
}

# 列出指定分类的镜像
function List-Category {
    param($Category)
    Write-Host "=== CyberPrism $($Category.ToUpper()) 类题目镜像 ===" -ForegroundColor Blue
    docker images | Select-String "cyberprism/$Category"
}

# 列出指定难度的镜像
function List-Difficulty {
    param($Difficulty)
    Write-Host "=== CyberPrism $($Difficulty.ToUpper()) 难度镜像 ===" -ForegroundColor Blue
    docker images | Select-String "cyberprism/.*-$Difficulty"
}

# 显示镜像详细信息
function Show-Info {
    param($ImageName)

    if (-not $ImageName) {
        Write-Host "错误: 请指定镜像名称" -ForegroundColor Red
        Write-Host "示例: .\manage-images.ps1 info cyberprism/web-easy:latest"
        exit 1
    }

    Write-Host "=== 镜像详细信息 ===" -ForegroundColor Blue
    docker inspect $ImageName
}

# 构建单个题目镜像
function Build-Challenge {
    param($ChallengeDir)

    if (-not $ChallengeDir) {
        Write-Host "错误: 请指定题目目录" -ForegroundColor Red
        Write-Host "示例: .\manage-images.ps1 build challenges\web-easy"
        exit 1
    }

    if (-not (Test-Path $ChallengeDir)) {
        Write-Host "错误: 目录不存在: $ChallengeDir" -ForegroundColor Red
        exit 1
    }

    $dockerComposePath = Join-Path $ChallengeDir "docker-compose.yml"
    if (-not (Test-Path $dockerComposePath)) {
        Write-Host "错误: 未找到 docker-compose.yml: $ChallengeDir" -ForegroundColor Red
        exit 1
    }

    Write-Host "正在构建镜像: $ChallengeDir" -ForegroundColor Green
    Push-Location $ChallengeDir
    docker-compose build
    Pop-Location
    Write-Host "✓ 镜像构建完成" -ForegroundColor Green
}

# 构建所有题目镜像
function Build-All {
    Write-Host "开始构建所有题目镜像..." -ForegroundColor Green

    Get-ChildItem -Path "challenges" -Directory | ForEach-Object {
        $dockerComposePath = Join-Path $_.FullName "docker-compose.yml"
        if (Test-Path $dockerComposePath) {
            Write-Host ""
            Write-Host "[$($_.Name)]" -ForegroundColor Yellow
            Build-Challenge $_.FullName
        }
    }

    Write-Host ""
    Write-Host "✓ 所有镜像构建完成" -ForegroundColor Green
}

# 清理悬空镜像
function Clean-Dangling {
    Write-Host "正在清理悬空镜像..." -ForegroundColor Yellow
    docker image prune -f
    Write-Host "✓ 悬空镜像已清理" -ForegroundColor Green
}

# 清理未使用的镜像
function Clean-Unused {
    Write-Host "正在清理未使用的镜像..." -ForegroundColor Yellow
    docker image prune -a -f
    Write-Host "✓ 未使用的镜像已清理" -ForegroundColor Green
}

# 删除所有CyberPrism镜像
function Clean-All {
    Write-Host "警告: 这将删除所有CyberPrism镜像！" -ForegroundColor Red
    $confirm = Read-Host "确定要继续吗? (yes/no)"

    if ($confirm -ne "yes") {
        Write-Host "操作已取消"
        exit 0
    }

    Write-Host "正在删除所有CyberPrism镜像..." -ForegroundColor Yellow
    $images = docker images -q 'cyberprism/*'
    if ($images) {
        docker rmi -f $images
    }
    Write-Host "✓ 所有CyberPrism镜像已删除" -ForegroundColor Green
}

# 显示统计信息
function Show-Stats {
    Write-Host "=== CyberPrism 镜像统计 ===" -ForegroundColor Blue
    Write-Host ""

    $total = (docker images -q 'cyberprism/*' | Measure-Object).Count
    Write-Host "总镜像数: " -NoNewline
    Write-Host "$total" -ForegroundColor Green

    Write-Host ""
    Write-Host "按分类统计:"
    @("web", "pwn", "crypto", "reverse", "misc") | ForEach-Object {
        $count = (docker images | Select-String "cyberprism/$_" | Measure-Object).Count
        if ($count -gt 0) {
            Write-Host "  $_: " -NoNewline
            Write-Host "$count" -ForegroundColor Green
        }
    }

    Write-Host ""
    Write-Host "按难度统计:"
    @("easy", "medium", "hard") | ForEach-Object {
        $count = (docker images | Select-String "cyberprism/.*-$_" | Measure-Object).Count
        if ($count -gt 0) {
            Write-Host "  $_: " -NoNewline
            Write-Host "$count" -ForegroundColor Green
        }
    }
}

# 主程序
param(
    [Parameter(Position=0)]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$Parameter
)

switch ($Command) {
    "list" { List-All }
    "list-web" { List-Category "web" }
    "list-pwn" { List-Category "pwn" }
    "list-crypto" { List-Category "crypto" }
    "list-reverse" { List-Category "reverse" }
    "list-easy" { List-Difficulty "easy" }
    "list-medium" { List-Difficulty "medium" }
    "list-hard" { List-Difficulty "hard" }
    "info" { Show-Info $Parameter }
    "build" { Build-Challenge $Parameter }
    "build-all" { Build-All }
    "clean-dangling" { Clean-Dangling }
    "clean-unused" { Clean-Unused }
    "clean-all" { Clean-All }
    "stats" { Show-Stats }
    "help" { Show-Help }
    default {
        Write-Host "错误: 未知命令 '$Command'" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
