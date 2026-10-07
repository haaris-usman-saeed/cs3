"""Functional smoke checks against both served and standalone course versions."""
from pathlib import Path
from functools import partial
import http.server
import threading
import shutil
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/'
errors = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=shutil.which('chromium'), args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url)
        expect(page.locator('h1')).to_contain_text('A label gives an answer')
        modules = page.evaluate('COURSE.modules.map(m => ({id:m.id,title:m.title}))')
        for module in modules:
            page.goto(url + '#' + module['id'])
            expect(page.locator('h1')).to_have_text(module['title'])
            assert page.locator('main svg').count() >= (0 if module['id'] in ['gradients','metrics','transfer','review'] else 1)
        print('PASS: all ten chapters render without JavaScript errors.')

        page.goto(url + '#recap')
        expect(page.locator('.lab-stats')).to_contain_text('0.45')
        page.get_by_role('button', name='Alternative: 1 + 2x').click()
        expect(page.locator('.lab-stats')).to_contain_text('0.50')
        page.get_by_role('button', name='Try the lecture’s 9-point grid').click()
        expect(page.locator('.search-message')).to_contain_text('9 evaluations')
        page.get_by_role('button', name='η = 1.1', exact=True).click()
        expect(page.locator('.rate-explanation')).to_contain_text('Magnitude grows')
        page.get_by_role('button', name='I can explain this without looking').click()
        expect(page.locator('#progress-count')).to_have_text('1 / 10')
        page.reload()
        expect(page.locator('#progress-count')).to_have_text('1 / 10')

        page.goto(url + '#classification')
        page.get_by_role('button', name='z = 4', exact=True).click()
        expect(page.locator('.sign-readout')).to_contain_text('0.982')
        expect(page.locator('.sign-readout')).to_contain_text('+1 · spam')

        page.goto(url + '#penguins')
        quiz = page.locator('#quiz-p-feature')
        quiz.get_by_role('button', name='Check answer').click()
        expect(quiz).to_contain_text('Enter or choose an answer first')
        quiz.locator('input[type=number]').fill('-0.5')
        quiz.get_by_role('button', name='Check answer').click()
        expect(quiz).to_contain_text('✓ Correct')

        page.goto(url + '#odds')
        expect(page.locator('.odds-readout')).to_contain_text('0.622')
        page.get_by_role('button', name='Set w = 0').click()
        expect(page.locator('.odds-explanation')).to_contain_text('The curve is flat')
        page.get_by_role('button', name='Lecture’s reported fitted model').click()
        expect(page.locator('#odds-b-out')).to_have_text('-1.639')
        expect(page.locator('#odds-w-out')).to_have_text('4.002')

        page.goto(url + '#loss')
        page.get_by_role('button', name='Lecture’s exact z = 0.5').click()
        expect(page.locator('.loss-readout')).to_contain_text('0.474')
        page.locator('#loss-y').select_option('0')
        expect(page.locator('.loss-readout')).to_contain_text('0.974')

        page.goto(url + '#gradients')
        page.get_by_role('button', name='Apply one simultaneous update').click()
        expect(page.locator('.one-coefficients')).to_contain_text('-0.0500')
        expect(page.locator('.one-coefficients')).to_contain_text('0.1000')

        page.goto(url + '#training')
        page.get_by_role('button', name='Go to 1000', exact=True).click()
        expect(page.locator('#train-iteration-out')).to_have_text('1000')
        expect(page.locator('.train-readout')).to_contain_text('4.117')
        expect(page.locator('.train-evaluation')).to_contain_text('TP 35, FP 4, FN 3, TN 41')
        page.get_by_role('button', name='Restart', exact=True).click()
        expect(page.locator('.train-readout')).to_contain_text('0.693')
        page.get_by_role('button', name='Play updates', exact=True).click()
        page.wait_for_timeout(200)
        assert int(page.locator('#train-iteration-out').text_content()) > 0
        page.get_by_role('button', name='Pause', exact=True).click()

        page.goto(url + '#metrics')
        page.locator('[data-cell=fn]').click()
        expect(page.locator('.cell-explanation')).to_contain_text('missed Gentoo')
        page.locator('#threshold-t').evaluate("el => { el.value='0.99'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        expect(page.locator('.threshold-stats')).to_contain_text('undefined')

        page.goto(url + '#review')
        page.get_by_role('button', name='Grade assessment').click()
        expect(page.locator('#exam-results')).to_contain_text('0 / 12 correct')
        answers = page.evaluate('EXAM.map(q => ({id:q.id,type:q.type,answer:q.answer}))')
        for q in answers:
            root = page.locator('#quiz-' + q['id'])
            if q.get('type') == 'numeric':
                root.locator('input[type=number]').fill(str(q['answer']))
            else:
                root.locator(f'input[value="{q["answer"]}"]').check()
        page.get_by_role('button', name='Grade assessment').click()
        expect(page.locator('#exam-results')).to_contain_text('12 / 12 correct')
        page.locator('[data-note=teach-sign]').fill('Hard labels discard progress within a class.')
        page.reload()
        expect(page.locator('[data-note=teach-sign]')).to_have_value('Hard labels discard progress within a class.')
        print('PASS: mathematical controls, quiz feedback, saved progress, notes, and assessment grading.')

        for route in ['formulas', 'lecture-map']:
            page.goto(url + '#' + route)
            expect(page.locator('h1')).to_be_visible()
        page.locator('[data-slide="66"]').click()
        expect(page.locator('#source-dialog')).to_be_visible()
        expect(page.locator('#source-image')).to_have_attribute('src', 'assets/slides/66.jpg')
        assert page.locator('#source-image').evaluate('el => el.complete && el.naturalWidth > 0')
        page.locator('#source-page').fill('68')
        page.locator('#source-page').press('Tab')
        expect(page.locator('#source-next')).to_be_disabled()
        page.locator('#source-close').click()
        print('PASS: formula reference, source map, and original slide navigation.')

        page.goto(url)
        page.screenshot(path='/tmp/logistic-lab-desktop.png', full_page=True)
        phone = browser.new_page(viewport={'width':390,'height':844}, is_mobile=True, has_touch=True)
        phone.on('pageerror', lambda error: errors.append(str(error)))
        for module in modules:
            phone.goto(url + '#' + module['id'])
            expect(phone.locator('h1')).to_have_text(module['title'])
            assert phone.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), module['id']
        phone.locator('#menu').click()
        phone.locator('#chapters a[href="#odds"]').click()
        expect(phone.locator('h1')).to_have_text('One prediction, four views')
        phone.screenshot(path='/tmp/logistic-lab-mobile.png', full_page=True)
        print('PASS: every lesson fits a 390 px screen; mobile navigation works.')

        offline = browser.new_page()
        offline.on('pageerror', lambda error: errors.append(str(error)))
        requests=[]
        offline.on('request', lambda request: requests.append(request.url))
        offline.goto(url+'dist/logistic-lab.html#odds')
        offline.context.set_offline(True)
        offline.evaluate("location.hash = '#loss'")
        expect(offline.locator('h1')).to_have_text('How wrong was that probability?')
        offline.evaluate("location.hash = '#odds'")
        expect(offline.locator('.odds-readout')).to_contain_text('0.622')
        offline.locator('[data-slide="39"]').click()
        assert offline.locator('#source-image').evaluate('el => el.complete && el.naturalWidth > 0')
        expect(offline.locator('#source-pdf')).to_have_attribute('download', 'lecture.pdf')
        assert requests == [url+'dist/logistic-lab.html']
        assert not errors, errors
        print('PASS: standalone HTML functions with network disabled after its initial load; slides are embedded and no further requests occur.')
        browser.close()
finally:
    server.shutdown()
