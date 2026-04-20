<%
    ftp = render_ctx['ftp.config']
    if ftp["banner"]:
        banner = ftp["banner"]
    else:
        banner = "Welcome to X-NAS FTP Server"

%>\
${banner}
