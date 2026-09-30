from core.models import ArchiveablePageAbstract
from django.http import JsonResponse, HttpResponse

from .models import TopicPage, ThemePage, ProjectPage

from articles.models import ArticlePage
from publications.models import PublicationPage
from multimedia.models import MultimediaPage
from events.models import EventPage

from core.models import ContentPage
from datetime import date
import csv
from urllib.parse import unquote


def all_topics(request):
    topics = TopicPage.objects.public().live().filter(archive=ArchiveablePageAbstract.ArchiveStatus.UNARCHIVED).order_by('title')
    return JsonResponse({
        'meta': {
            'total_count': topics.count(),
        },
        'items': [{
            'id': topic.id,
            'title': topic.title,
            'url': topic.get_url(request),
        } for topic in topics[:100]],
    }, safe=False)


def topic_contentpages(request):
    topics = TopicPage.objects.live().filter(archive=0).order_by('title')
    results = []

    for topic in topics:
        results.append({
            "name": topic.title,
            "content_pages": topic.content_pages.count(),
            "children": [
                {
                    "name": "Articles",
                    "value": ArticlePage.objects.filter(topics__in=[topic.id]).count(),
                },
                {
                    "name": "Publications",
                    "value": PublicationPage.objects.filter(topics__in=[topic.id]).count(),
                },
                {
                    "name": "Multimedia",
                    "value": MultimediaPage.objects.filter(topics__in=[topic.id]).count(),
                },
                {
                    "name": "Events",
                    "value": EventPage.objects.filter(topics__in=[topic.id]).count(),
                },
            ],
        })

    return JsonResponse({
        "name": "Topics",
        "children": results,
    })


def overlapping_topics_verification(request):
    topics = {
        'Digital Economy': ['Central Banking', 'Digital Currency'],
        'Geopolitics': ['Africa', 'China', 'India'],
        'Multilateral Institutions': ['IMF', 'NAFTA/CUSMA', 'WTO'],
        'Platform Governance': ['Platform Governance', 'Internet Governance'],
        'Transformative Technologies': ['Emerging Technology', 'Innovation', 'Innovation Economy'],
    }

    results = []

    for new_topic_title, old_topic_titles in topics.items():
        old_topics = []
        no_longer_exists = []

        for old_topic_title in old_topic_titles:
            if TopicPage.objects.filter(title=old_topic_title).exists():
                old_topics.append(TopicPage.objects.get(title=old_topic_title))
            else:
                no_longer_exists.append(old_topic_title)

        content_pages = list(set(ContentPage.objects.filter(topics__in=old_topics)))

        results.append({
            "new_topic": new_topic_title,
            "targeted_old_topics": ', '.join(old_topic_titles),
            "topic_no_longer_exists": ', '.join(no_longer_exists),
            "content_pages": len(content_pages),
        })

    return JsonResponse({
        "name": "Overlapping Topics",
        "children": results,
    })


def themes(request):
    themes = ThemePage.objects.live().filter(archive=0).order_by('title')
    results = []

    for theme in themes:
        topic_pages = TopicPage.objects.filter(program_theme=theme)
        content_pages = []

        for topic in topic_pages:
            content_pages += topic.content_pages.all()

        results.append({
            "name": theme.title,
            "content_pages": len(list(set(content_pages))),
        })

    return JsonResponse({
        "name": "Themes",
        "children": results,
    })


def programs(request):
    themes = ThemePage.objects.live().filter(archive=0).order_by('title')
    theme_results = []

    for theme in themes:
        topic_pages = TopicPage.objects.filter(program_theme=theme)
        topic_results = []

        for topic in topic_pages:
            program_pages = ProjectPage.objects.filter(topics__in=[topic])
            program_results = []

            for program in program_pages:
                program_results.append({
                    "name": program.title,
                    "value": program.content_pages.count(),
                })

            topic_results.append({
                "name": topic.title,
                "children": program_results,
            })

        theme_results.append({
            "name": theme.title,
            "children": topic_results,
        })

    return JsonResponse({
        "name": "Themes",
        "children": theme_results,
    })


def program_content_within_range(request):
    start_date = date(2024, 8, 1)
    end_date = date(2025, 7, 31)
    themes = ThemePage.objects.live().filter(archive=0).order_by('title')
    results = []

    for theme in themes:
        topic_pages = TopicPage.objects.filter(program_theme=theme)
        theme_content_pages = []

        for topic in topic_pages:
            all_slugs = list(
                topic.content_pages.live().filter(
                    publishing_date__gte=start_date,
                    publishing_date__lte=end_date
                ).values_list('slug', flat=True)
            )
            theme_content_pages += all_slugs

        results.append({
            "name": theme.title,
            "all_content_pages": list(set(theme_content_pages)),
        })

    return JsonResponse({
        "name": "Themes",
        "children": results,
    })


def program_affiliates(request):
    def convert_youtube(url):
        if url and "youtu.be/" in url:
            return url.replace("https://youtu.be/", "https://www.youtube.com/watch?v=")
        return url

    request_type = request.GET.get('type')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write('\ufeff')

    pages_list = []
    authors_list = []
    projects = ProjectPage.objects.live().filter(archive=0).order_by('title')

    for project in projects:
        # include landing page (no video url for project)
        url = unquote(project.url)
        if url.startswith("https://www.cigionline.org"):
            url = url[len("https://www.cigionline.org"):]
        pages_list.append({
            'program': project.title,
            'title': project.title,
            'url': url,
            'pdf': '',
            'video_url': '',
        })

        # pull content pages
        content_pages = project.content_pages.live().all()
        authors = []

        for page in content_pages:
            # normalise page url once
            url = unquote(page.url)
            if url.startswith("https://www.cigionline.org"):
                url = url[len("https://www.cigionline.org"):]

            # try to grab multimedia_url from the specific page
            multimedia_url = getattr(page.specific, 'multimedia_url', '') or ''
            multimedia_url = convert_youtube(unquote(multimedia_url)) if multimedia_url else ''

            if hasattr(page.specific, 'pdf_downloads'):
                for pdf in page.specific.pdf_downloads:
                    pdf_url = unquote(pdf.value['file'].url) if pdf.value['file'] else ''
                    if not pdf_url.startswith("https://www.cigionline.org"):
                        pdf_url = f'https://www.cigionline.org{pdf_url}'
                    pages_list.append({
                        'program': project.title,
                        'title': page.title,
                        'url': url,
                        'pdf': pdf_url,
                        'video_url': multimedia_url,
                    })
            else:
                pages_list.append({
                    'program': project.title,
                    'title': page.title,
                    'url': url,
                    'pdf': '',
                    'video_url': multimedia_url,
                })

            authors += [author for author in getattr(page.specific, 'authors', None).all()]

        for author in list(set(authors)):
            url = unquote(author.author.url) if author.author.url else ''
            if url.startswith("https://www.cigionline.org"):
                url = url[len("https://www.cigionline.org"):]
            authors_list += [{
                'program': project.title,
                'name': author.author.title,
                'url': url,
            }]

    # request experts
    if request_type == 'experts':
        response['Content-Disposition'] = 'attachment; filename="program_experts.csv"'
        writer = csv.writer(response)
        writer.writerow(['Programs', 'Expert', 'URL'])      # CSV header
        for author in authors_list:
            writer.writerow([author['program'], author['name'], author['url']])
        return response

    # default to content page requests
    response['Content-Disposition'] = 'attachment; filename="program_pages.csv"'
    writer = csv.writer(response)
    writer.writerow(['Programs', 'Title', 'Page URL', 'Link URL', 'Video URL'])     # CSV header
    for page in pages_list:
        writer.writerow([
            page['program'],
            page['title'],
            page['url'],
            page['pdf'],
            page['video_url'],
        ])

    return response


def topic_updates_verification(request):
    page_ids = [
        125, 170, 267, 300, 402, 430, 572, 577, 583, 584, 587, 684, 687, 688,
        694, 697, 707, 711, 714, 741, 747, 778, 782, 793, 823, 854, 888, 898,
        933, 936, 987, 1007, 1151, 1160, 1174, 1244, 1251, 1254, 1268, 1307,
        1317, 1332, 1359, 1361, 1399, 1401, 1404, 1406, 1409, 1412, 1449,
        1455, 1468, 1522, 1545, 1553, 1555, 1611, 1619, 1648, 1672, 1683,
        1685, 1689, 1694, 1696, 1709, 1738, 1878, 1882, 1896, 1898, 2035,
        2041, 2057, 2081, 2111, 2127, 2163, 2167, 2170, 3308, 3399, 3494,
        3522, 3525, 3526, 3551, 3553, 3558, 3565, 3607, 3621, 3681, 3708,
        3726, 3734, 3759, 3782, 3799, 3800, 3806, 3814, 3823, 3893, 3897,
        3903, 3931, 3969, 3971, 3980, 3987, 4000, 4005, 4006, 4007, 4011,
        4033, 4036, 4038, 4039, 4054, 4062, 4076, 4082, 4099, 4620, 4660,
        4661, 4662, 4663, 4665, 4666, 4668, 4669, 4670, 4680, 4697, 4705,
        4707, 4728, 4730, 4735, 4799, 4805, 4816, 4820, 5024, 5075, 5089,
        5095, 5105, 5124, 5135, 5168, 5170, 5197, 5206, 5225, 5226, 5236,
        5242, 5249, 10865, 10927, 10932, 10934, 10936, 10942, 10943, 10946,
        10947, 10949, 10952, 10953, 10954, 10962, 11077, 11097, 11101, 11105,
        11110, 11126, 11151, 11153, 11155, 11157, 11158, 11159, 11160, 11163,
        11165, 11166, 11167, 11168, 11173, 11184, 11192, 11197, 11198, 11222,
        11228, 11231, 11235, 11252, 11332, 11352, 11353, 11354, 11358, 11359,
        11361, 11363, 11364, 11368, 11372, 11376, 11378, 11384, 11388, 11409,
        11411, 11417, 11420, 12294, 12297, 12304, 12331, 12335, 12337, 12339,
        12340, 12342, 12343, 12345, 12346, 12347, 12348, 12355, 12418, 12523,
        12843, 12844, 12849, 12875, 12880, 12888, 12956, 12967, 12985, 12990,
        12992, 13038, 13064, 13092, 13094, 13095, 13101, 13107, 13109, 13120,
        13122, 13124, 13125, 13131, 13133, 13134, 13136, 13151, 13253, 13255,
        13380, 13420, 13447, 13449, 13450, 13452, 13460, 13464, 13465, 13467,
        13468, 13477, 13507, 13527, 13552, 13590, 13611, 13616, 13642, 13659,
        13662, 13665, 13667, 13669, 13670, 13674, 13675, 13677, 13685, 13700,
        13701, 13702, 13704, 13706, 13711, 13713, 13714, 13715, 13717, 13719,
        13721, 13723, 13724, 13726, 13727, 13728, 13729, 13732, 13733, 13734,
        13736, 13737, 13738, 13739, 13743, 13744, 13811, 13880, 13914, 13918,
        13946, 13980, 13983, 14000, 14004, 14008, 14012, 14021, 14045, 14068,
        14086, 14092, 14104, 14126, 14144, 14146, 14147, 14149, 14150, 14151,
        14154, 14155, 14156, 14158, 14160, 14161, 14163, 14165, 14168, 14171,
        14172, 14173, 14174, 14176, 14184, 14224, 14269, 14274, 14275, 14278,
        14281, 14284, 14294, 14296, 14304, 14310, 14326, 14341, 14345, 14386,
        14405, 14428, 14443, 14454, 14481, 14497, 14501, 14508, 14510, 14511,
        14512, 14514, 14518, 14519, 14522, 14557, 14562, 14588, 14616, 14644,
        14645, 14667, 14673, 14674, 14680, 14689, 14711, 14722, 14736, 14744,
        14751, 14767, 14786, 14788, 14806, 14810, 14813, 14815, 14820, 14821,
        14853, 14854, 14856, 14858, 14861, 14866, 14867, 14868, 14888, 14889,
        14890, 14892, 14893, 14894, 14905, 14949, 14952, 15005, 15009, 15029,
        15035, 15045, 15051, 15054, 15055, 15057, 15059, 15070, 15075, 15078,
        15084, 15087, 15123, 15125, 15136, 15146, 15148, 15150, 15155, 15160,
        15165, 15172, 15181, 15185, 15187, 15196, 15198, 15199, 15201, 15202,
        15213, 15236, 15237, 15242, 15244, 15245, 15247, 15263, 15268, 15270,
        15328, 15329, 15336, 15341, 15349, 15362, 15380, 15384, 15387, 15388,
        15392, 15399, 15408, 15412, 15413, 15414, 15419, 15426, 15440, 15446,
        15450, 15454, 15463, 15464, 15468, 15471, 15472, 17302, 19789, 19790,
        19804, 19805, 19808, 19823, 19862, 19874, 19883, 19916, 19921, 19925,
        19929, 19935, 19949, 20000, 20030, 20031, 20062, 20064, 20117, 20120,
        20123, 20146, 20150, 20165, 20168, 20169, 20174, 20226, 20247, 20334,
        20335, 20338, 20355, 20377, 20416, 20418, 20419, 20443, 20444, 20462,
        20493, 20515, 20537, 20538, 20541, 20547, 20587, 20590, 20601, 20615,
        20617, 20627, 20634, 20638, 20643, 20644, 20663, 20672, 20673, 20679,
        20680, 20685, 20725, 20726, 20743, 20745, 20752, 20753, 20760, 20765,
        20767, 20768, 20770, 20773, 20775, 20777, 20780, 20784, 20810, 20811,
        20851, 20853, 20858, 20861, 20875, 20876, 20879, 20882, 20883, 20884,
        20893, 20894, 20897, 20899, 20901, 20902, 20906, 20910, 20911, 20912,
        20914, 20924, 20930, 20937, 20952, 20957, 20960, 20965, 20970, 21008,
        21013, 21014, 21017, 21040, 21045, 21056, 21061, 21068, 21072, 21115,
        21130, 21133, 21134, 21135, 21137, 21160, 21161, 21172, 21173, 21175,
        21176, 21177, 21178, 21179, 21191, 21195, 21247, 21249, 21265, 21270,
        21304, 21328, 21330, 21333, 21336, 21338, 21371, 21380, 21383, 21386,
        21387, 21400, 21401, 21437, 21455, 21497, 21499, 21502, 21504, 21508,
        21510, 21541, 21542, 21548, 21552, 21554, 21561, 21566, 21573, 21574,
        21580, 21581, 21583, 21589, 21591, 21596, 21634, 21647, 21656, 21662,
        21685, 21686, 21693, 21699, 21706, 21710, 21713, 21715, 21716, 21718,
        21756, 21824, 21837, 21842, 21850, 21855, 21857, 21860, 21864, 22119,
        22131, 22144, 22151, 22153, 22154, 22192, 22193, 22213, 22218, 22221,
        22222, 22227, 22232, 22237, 22249, 22255, 22280, 22288, 22290, 22295,
        22297, 22300, 22305, 22314, 22316, 22318, 22332, 22389, 22391, 22392,
        22396, 22397, 22432, 22446, 22448, 22485, 22487, 22494, 22501, 22505,
        22513, 22516, 22517, 22523, 22526, 22530, 22533, 22534, 22535, 22538,
        22540, 22544, 22593, 22597, 22598, 22600, 22601, 22604, 22613, 22614,
        22617, 22618, 22622, 22624, 22629, 22630, 22633, 22638, 22641, 22642,
        22653, 22654, 22656, 22660, 22661, 22663, 22671, 22675, 22681, 22685,
        22688, 22689, 22692, 22694, 22701, 22704, 22791, 22795, 22799, 22800,
        22821, 22855, 22858, 22866, 22867, 22868, 22869, 22870, 22871, 22872,
        22876, 22879, 22891, 22893, 22894, 22895, 22914, 22916, 22917, 22923,
        22924, 22925, 22929, 22933, 22937, 22940, 22941, 22942, 22946, 22947,
        22948, 22953, 22956, 22959, 22960, 22970, 22998, 23001, 23010, 23016,
        23018, 23022, 23051, 23055, 23056, 23058, 23059, 23092, 23096, 23097,
        23099, 23101, 23106, 23109, 23113, 23114, 23115, 23119, 23121, 23125,
        23153, 23156, 23160, 23163, 23166, 23169, 23177, 23179, 23200, 23207,
        23257, 23258, 23259, 23263, 23265, 23269, 23271, 23274, 23276, 23285,
        23294, 23296, 23298, 23344, 23349, 23350, 23360, 23375, 23376, 23387,
        23388, 23398, 23432, 23434, 23441, 23443, 23444, 23445, 23447, 23451,
        23452, 23465, 23470, 23471, 23475, 23478, 23479, 23483, 23485, 23498,
        23508, 23513, 23515, 23516, 23518, 23524, 23528, 23536, 23537, 23540,
        23545, 23559, 23560, 23566, 23568, 23574, 23578, 23579, 23581, 23583,
        23621, 23624, 23630, 23631, 23632, 23643, 23651, 23656, 23661, 23664,
        23665, 23674, 23681, 23684, 23685, 23687, 23689, 23690, 23691, 23695,
        23697, 23698, 23699, 23700, 23701, 23702, 23703, 23704, 23705, 23706,
        23707, 23708, 23710, 23711, 23712, 23713, 23714, 23716, 23717, 23718,
        23719, 23720, 23721, 23723, 23724, 23725, 23727, 23728, 23729, 23730,
        23731, 23769, 23811, 23812,
    ]

    pages = (
        ContentPage.objects
        .filter(id__in=page_ids)
        .prefetch_related("topics")
        .order_by("id")
    )

    response = HttpResponse(
        content_type="text/csv; charset=utf-8"
    )
    response["Content-Disposition"] = 'attachment; filename="page_topics.csv"'
    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow([
        "page_id",
        "title",
        "url",
        "topics",
    ])

    for page in pages:
        topics = "; ".join(
            page.topics
            .order_by("title")
            .values_list("title", flat=True)
        )

        writer.writerow([
            page.id,
            page.title,
            page.full_url or page.url or "",
            topics,
        ])

    return response
