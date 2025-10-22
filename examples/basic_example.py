"""
Basic example of using StepWright to scrape a simple webpage.

This example demonstrates:
- Basic navigation
- Scrolling and waiting
- Data extraction using different selectors (tag, xpath)
- Running with headless browser
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from stepwright import run_scraper, TabTemplate, BaseStep, RunOptions


async def basic_example():
    """Basic web scraping example"""
    templates = [
        TabTemplate(
            tab='example',
            steps=[
                BaseStep(
                    id='navigate',
                    action='navigate',
                    value='http://example.com/'
                ),
                BaseStep(
                    id='wait_for_page',
                    action='scroll',
                    value='100',
                    wait=2000
                ),
                BaseStep(
                    id='get_title',
                    action='data',
                    object_type='tag',
                    object='h1',
                    key='title',
                    data_type='text'
                ),
                BaseStep(
                    id='get_description',
                    action='data',
                    object_type='xpath',
                    object='/html/body/div/p[1]',
                    key='description',
                    data_type='text'
                )
            ]
        )
    ]

    try:
        print('🚀 Starting scraper...')
        
        results = await run_scraper(templates, RunOptions(
            browser={
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            }
        ))
        
        # If you want headful browser:
        # results = await run_scraper(templates, RunOptions(
        #     browser={
        #         'headless': False
        #     }
        # ))
        
        print('✅ Scraping completed!')
        print('📊 Results:', json.dumps(results, indent=2))
        
    except Exception as error:
        print(f'❌ Error: {error}')
        raise


# Run the example
if __name__ == '__main__':
    asyncio.run(basic_example())

