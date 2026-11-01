from pathlib import Path
p=Path('tests/test_ui.py');s=p.read_text().replace("AppTest.from_file('app.py')","AppTest.from_file('app.py', default_timeout=15)");p.write_text(s)
p=Path('.build/build_book.py');s=p.read_text().replace('aside input{','aside label{display:block;margin-top:16px}aside input{').replace('.copy{float:right;','.copy{display:block;margin-left:auto!important;');p.write_text(s)
