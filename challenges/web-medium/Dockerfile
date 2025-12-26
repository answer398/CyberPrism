FROM php:8.1-apache

# 复制文件
COPY ./src /var/www/html/

# 设置权限
RUN chown -R www-data:www-data /var/www/html

# 创建flag文件
RUN echo "Placeholder for FLAG" > /flag.txt && chmod 644 /flag.txt

# 暴露端口
EXPOSE 80
