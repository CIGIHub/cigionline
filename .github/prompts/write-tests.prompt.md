---
description: "Write pytest tests for a Django/Wagtail feature in this project"
argument-hint: "Describe the feature or code path to test"
agent: "agent"
---

Write tests for the following feature or code path in this codebase:

$input

## Testing Conventions

**Framework**: pytest (`python -m pytest`) — tests live in each app's `tests.py`.

**Test class patterns**:
- `SimpleTestCase` for template/rendering tests that don't need the DB
- `TestCase` for anything requiring ORM access
- Use `@patch("module.path.function_name")` to mock external calls (SendGrid, Celery tasks, etc.)

**Wagtail page setup** (needed for any page model test):
```python
from wagtail.models import Site

root = Site.objects.get(is_default_site=True).root_page
page = MyPage(title="Test Page")
root.add_child(instance=page)
page.save_revision().publish()
```

**HTTP tests** — use `self.client.post(page.url + 'sub-route/', data={...})` for routable page routes.

**Template tests** — use `render_to_string("template/path.html", context)` with `SimpleNamespace` or minimal mock objects.

**Mocking** — always patch at the point of use, not the point of definition:
```python
@patch("events.models.send_confirmation_email")
def test_something(self, mock_send):
    ...
    mock_send.assert_called_once()
```

## What to cover
- Happy path (valid input, expected outcome)
- Edge cases (boundary values, empty/null inputs)
- Error paths (invalid input, capacity full, duplicate registration, etc.)
- Any conditional logic branches

## After writing tests
Run them to confirm they pass:
```
python -m pytest <app>/tests.py -x --tb=short -q
```

Fix any failures before finishing.
