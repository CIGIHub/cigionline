from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from wagtail import blocks

from streams.blocks import ButtonBlock, InteractiveChartBlock


class ButtonBlockTests(SimpleTestCase):
    def test_requires_page_or_url(self):
        with self.assertRaises(blocks.StructBlockValidationError):
            ButtonBlock().clean({
                'text': 'Read more',
                'page': None,
                'url': '',
            })


class InteractiveChartBlockTests(SimpleTestCase):
    def setUp(self):
        self.block = InteractiveChartBlock()

    def test_parses_multiple_data_series(self):
        parsed = self.block.parse_csv(
            'Year,Revenue,Expenses\n2024,12.5,8\n2025,15,9'
        )

        self.assertEqual(parsed['headers'], ['Year', 'Revenue', 'Expenses'])
        self.assertEqual(parsed['labels'], ['2024', '2025'])
        self.assertEqual(parsed['series'], [[12.5, 15], [8, 9]])

    def test_allows_missing_data_points(self):
        parsed = self.block.parse_csv('Year,Revenue\n2024,\n2025,15')

        self.assertEqual(parsed['series'], [[None, 15]])

    def test_rejects_non_numeric_data(self):
        with self.assertRaisesMessage(ValidationError, 'row 2, column 2 must be a number'):
            self.block.parse_csv('Year,Revenue\n2024,nope')

    def test_rejects_inconsistent_rows(self):
        with self.assertRaisesMessage(ValidationError, 'row 2 has 2 columns; expected 3'):
            self.block.parse_csv('Year,Revenue,Expenses\n2024,12')

    def test_allows_up_to_one_thousand_data_rows(self):
        csv_data = 'Index,Value\n' + '\n'.join(f'{index},{index}' for index in range(1000))

        parsed = self.block.parse_csv(csv_data)

        self.assertEqual(len(parsed['table_rows']), 1000)

    def test_rejects_more_than_one_thousand_data_rows(self):
        csv_data = 'Index,Value\n' + '\n'.join(f'{index},{index}' for index in range(1001))

        with self.assertRaisesMessage(ValidationError, 'more than 1,000 data rows'):
            self.block.parse_csv(csv_data)

    def test_renders_chart_config_and_accessible_table(self):
        value = self.block.to_python({
            'title': 'Annual revenue',
            'description': 'Revenue increased.',
            'caption': 'Source: CIGI',
            'chart_type': 'bar',
            'csv_data': 'Year,Revenue\n2024,12',
            'full_width': False,
        })

        html = self.block.render(value)

        self.assertIn('class="interactive-chart"', html)
        self.assertIn('aria-labelledby=', html)
        self.assertIn('type="application/json"', html)
        self.assertIn('<th scope="row">2024</th>', html)
