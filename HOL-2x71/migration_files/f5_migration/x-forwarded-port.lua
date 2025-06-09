XFProto = avi.http.get_header("X-Forwarded-Proto")
XFPort = avi.http.get_header("X-Forwarded-Port")

if XFProto then
      avi.http.replace_header("X-Forwarded-Proto", avi.http.protocol())
end
if XFPort then
      avi.http.replace_header("X-Forwarded-Port", avi.vs.client_port())
end