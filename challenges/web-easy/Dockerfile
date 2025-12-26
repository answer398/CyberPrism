FROM php:8.1-apache

# 安装MySQL扩展
RUN docker-php-ext-install mysqli pdo pdo_mysql

# 复制文件
COPY ./src /var/www/html/

# 设置权限
RUN chown -R www-data:www-data /var/www/html

# 暴露端口
EXPOSE 80
