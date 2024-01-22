backend static_files {
    .host = "cigionline-static-staging.s3.amazonaws.com";
    .port = "80";
}

sub vcl_recv {
    # Redirect requests for static files
    if (req.url ~ "^/static/") {
        set req.backend_hint = application.backend();
    }
}
