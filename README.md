# IPv6Relay

###Function

Host-A 在IPv6 Only的网络环境下，Host-B 在IPv4, IPv6双栈的网络环境下。  
IPv6Relay的作用是在Host-B上搭建Socks5的Server，在Host-A监听127.0.0.1:1080，将TCP socket 通过IPv6网络relay到Host-B上。\n使得Host-A可以通过Host-B访问IPv4网络。（仅支持TCP）

###Usage
在Host-B上运行socks5.py: socks5.py Host-B_IPv6Address Port Password  
在Host-A上运行ipv6relay.py: ipv6relay.pu Host-B_IPv6Address Port Password  
可以设置浏览器通过 127.0.0.1:1080 代理访问，或者将系统socks5代理设置为 127.0.0.1:1080 (设置系统代理可以使所有软件的TCP socket都走代理)
