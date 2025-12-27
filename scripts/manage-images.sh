#!/bin/bash
# CyberPrism Docker镜像管理脚本
# 用于快速管理和查看CyberPrism平台的Docker镜像

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${GREEN}CyberPrism Docker镜像管理工具${NC}"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  list                    列出所有CyberPrism镜像"
    echo "  list-web                列出所有Web类题目镜像"
    echo "  list-pwn                列出所有Pwn类题目镜像"
    echo "  list-easy               列出所有简单难度镜像"
    echo "  list-medium             列出所有中等难度镜像"
    echo "  list-hard               列出所有困难难度镜像"
    echo "  info <镜像名>           显示镜像详细信息"
    echo "  build <题目目录>        构建指定题目的镜像"
    echo "  build-all               构建所有题目镜像"
    echo "  clean-dangling          清理悬空镜像"
    echo "  clean-unused            清理所有未使用的镜像"
    echo "  clean-all               删除所有CyberPrism镜像"
    echo "  stats                   显示镜像统计信息"
    echo ""
    echo "示例:"
    echo "  $0 list"
    echo "  $0 list-web"
    echo "  $0 info cyberprism/web-easy:latest"
    echo "  $0 build challenges/web-easy"
    echo "  $0 build-all"
    echo "  $0 clean-dangling"
}

# 列出所有CyberPrism镜像
list_all() {
    echo -e "${BLUE}=== 所有CyberPrism镜像 ===${NC}"
    docker images --filter=reference='cyberprism/*' --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

# 列出指定分类的镜像
list_category() {
    local category=$1
    echo -e "${BLUE}=== CyberPrism ${category^^} 类题目镜像 ===${NC}"
    docker images | grep "cyberprism/${category}" | awk '{printf "%-40s %-20s %-15s\n", $1, $2, $7}'
}

# 列出指定难度的镜像
list_difficulty() {
    local difficulty=$1
    echo -e "${BLUE}=== CyberPrism ${difficulty^^} 难度镜像 ===${NC}"
    docker images | grep "cyberprism/.*-${difficulty}" | awk '{printf "%-40s %-20s %-15s\n", $1, $2, $7}'
}

# 显示镜像详细信息
show_info() {
    local image=$1
    if [ -z "$image" ]; then
        echo -e "${RED}错误: 请指定镜像名称${NC}"
        echo "示例: $0 info cyberprism/web-easy:latest"
        exit 1
    fi

    echo -e "${BLUE}=== 镜像详细信息 ===${NC}"
    docker inspect "$image" --format '
镜像ID: {{.Id}}
创建时间: {{.Created}}
大小: {{.Size}} bytes
架构: {{.Architecture}}
操作系统: {{.Os}}
标签:{{range .RepoTags}}
  - {{.}}{{end}}
环境变量:{{range .Config.Env}}
  - {{.}}{{end}}
暴露端口:{{range $port, $_ := .Config.ExposedPorts}}
  - {{$port}}{{end}}
'
}

# 构建单个题目镜像
build_challenge() {
    local challenge_dir=$1
    if [ -z "$challenge_dir" ]; then
        echo -e "${RED}错误: 请指定题目目录${NC}"
        echo "示例: $0 build challenges/web-easy"
        exit 1
    fi

    if [ ! -d "$challenge_dir" ]; then
        echo -e "${RED}错误: 目录不存在: $challenge_dir${NC}"
        exit 1
    fi

    if [ ! -f "$challenge_dir/docker-compose.yml" ]; then
        echo -e "${RED}错误: 未找到 docker-compose.yml: $challenge_dir${NC}"
        exit 1
    fi

    echo -e "${GREEN}正在构建镜像: $challenge_dir${NC}"
    cd "$challenge_dir" || exit 1
    docker-compose build
    cd - > /dev/null || exit 1
    echo -e "${GREEN}✓ 镜像构建完成${NC}"
}

# 构建所有题目镜像
build_all() {
    echo -e "${GREEN}开始构建所有题目镜像...${NC}"

    for dir in challenges/*/; do
        if [ -f "${dir}docker-compose.yml" ]; then
            echo ""
            echo -e "${YELLOW}[$(basename "$dir")]${NC}"
            build_challenge "$dir"
        fi
    done

    echo ""
    echo -e "${GREEN}✓ 所有镜像构建完成${NC}"
}

# 清理悬空镜像
clean_dangling() {
    echo -e "${YELLOW}正在清理悬空镜像...${NC}"
    docker image prune -f
    echo -e "${GREEN}✓ 悬空镜像已清理${NC}"
}

# 清理未使用的镜像
clean_unused() {
    echo -e "${YELLOW}正在清理未使用的镜像...${NC}"
    docker image prune -a -f
    echo -e "${GREEN}✓ 未使用的镜像已清理${NC}"
}

# 删除所有CyberPrism镜像
clean_all() {
    echo -e "${RED}警告: 这将删除所有CyberPrism镜像！${NC}"
    read -p "确定要继续吗? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "操作已取消"
        exit 0
    fi

    echo -e "${YELLOW}正在删除所有CyberPrism镜像...${NC}"
    docker rmi -f $(docker images -q 'cyberprism/*') 2>/dev/null
    echo -e "${GREEN}✓ 所有CyberPrism镜像已删除${NC}"
}

# 显示统计信息
show_stats() {
    echo -e "${BLUE}=== CyberPrism 镜像统计 ===${NC}"
    echo ""

    total=$(docker images -q 'cyberprism/*' | wc -l)
    echo -e "总镜像数: ${GREEN}$total${NC}"

    echo ""
    echo "按分类统计:"
    for category in web pwn crypto reverse misc; do
        count=$(docker images | grep "cyberprism/${category}" | wc -l)
        if [ "$count" -gt 0 ]; then
            echo -e "  ${category}: ${GREEN}$count${NC}"
        fi
    done

    echo ""
    echo "按难度统计:"
    for difficulty in easy medium hard; do
        count=$(docker images | grep "cyberprism/.*-${difficulty}" | wc -l)
        if [ "$count" -gt 0 ]; then
            echo -e "  ${difficulty}: ${GREEN}$count${NC}"
        fi
    done

    echo ""
    total_size=$(docker images --filter=reference='cyberprism/*' --format "{{.Size}}" | sed 's/MB//g' | sed 's/GB/*1024/g' | bc | awk '{sum+=$1} END {printf "%.2f MB", sum}')
    echo -e "总大小: ${GREEN}$total_size${NC}"
}

# 主程序
case "$1" in
    list)
        list_all
        ;;
    list-web)
        list_category "web"
        ;;
    list-pwn)
        list_category "pwn"
        ;;
    list-crypto)
        list_category "crypto"
        ;;
    list-reverse)
        list_category "reverse"
        ;;
    list-easy)
        list_difficulty "easy"
        ;;
    list-medium)
        list_difficulty "medium"
        ;;
    list-hard)
        list_difficulty "hard"
        ;;
    info)
        show_info "$2"
        ;;
    build)
        build_challenge "$2"
        ;;
    build-all)
        build_all
        ;;
    clean-dangling)
        clean_dangling
        ;;
    clean-unused)
        clean_unused
        ;;
    clean-all)
        clean_all
        ;;
    stats)
        show_stats
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
