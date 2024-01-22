sub vcl_recv {
    # Redirect requests for static files
    if (req.url ~ "^/static/") {
        set req.backend_hint = application.backend();
    }
    set req.backend_hint = application.backend();
}
