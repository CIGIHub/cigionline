backend static_files {
    .host = "cigionline-static-staging.s3.amazonaws.com";
    .port = "443";
}

sub vcl_recv {
    # Redirect requests for static files
    if (req.url ~ "^/static/") {
        set req.backend_hint = static_files.backend();
    } else {
        set req.backend_hint = application.backend();
    }
}
