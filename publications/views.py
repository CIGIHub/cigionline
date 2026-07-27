import csv

from django.http import HttpResponse
from wagtail.models import Site

from .models import PublicationPage


def publications_by_type(request):
    site = Site.find_for_request(request)

    publications = (
        PublicationPage.objects
        .live()
        .public()
        .descendant_of(site.root_page)
        .select_related("publication_type")
        .order_by("-publishing_date")
    )

    response = HttpResponse(
        content_type="text/csv; charset=utf-8",
    )
    response["Content-Disposition"] = (
        'attachment; filename="publications.csv"'
    )

    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow(
        [
            "title",
            "publishing_date",
            "url",
            "publication_type",
            "pdf_downloads",
        ]
    )

    for publication in publications:
        pdf_filenames = []

        for block in publication.pdf_downloads:
            if block.block_type != "pdf_download":
                continue

            document = block.value.get("file")

            if document:
                pdf_filenames.append(document.filename)

        writer.writerow(
            [
                publication.title,
                (
                    publication.publishing_date.isoformat()
                    if publication.publishing_date
                    else ""
                ),
                publication.get_full_url(request),
                (
                    publication.publication_type.title
                    if publication.publication_type
                    else ""
                ),
                "; ".join(pdf_filenames),
            ]
        )

    return response
