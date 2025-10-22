"""
Advanced example of using StepWright with pagination and streaming results.

This example demonstrates:
- Initial setup steps (initSteps)
- Per-page data collection (perPageSteps)
- ForEach loops for multiple items
- Pagination with next button
- XPath selectors
- Streaming results with callbacks
- Complex data extraction
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from stepwright import (
    run_scraper,
    run_scraper_with_callback,
    TabTemplate,
    BaseStep,
    PaginationConfig,
    NextButtonConfig,
    RunOptions
)


async def advanced_example():
    """Advanced web scraping example with pagination"""
    templates = [
        TabTemplate(
            tab='news_scraper',
            initSteps=[
                BaseStep(
                    id='navigate_to_news',
                    action='navigate',
                    value='https://news.ycombinator.com'
                ),
                BaseStep(
                    id='wait_for_page',
                    action='scroll',
                    value='100',
                    wait=3000
                )
            ],
            perPageSteps=[
                BaseStep(
                    id='get_articles',
                    action='foreach',
                    object_type='xpath',
                    object='//tr[contains(@class, "athing")]',
                    subSteps=[
                        BaseStep(
                            id='get_title',
                            action='data',
                            object_type='class',
                            object='titleline',
                            key='title',
                            data_type='text'
                        ),
                        BaseStep(
                            id='get_link',
                            action='data',
                            object_type='xpath',
                            object='.//span[@class="titleline"]/a/@href',
                            key='link',
                            data_type='attribute'
                        ),
                        BaseStep(
                            id='get_score',
                            action='data',
                            object_type='xpath',
                            object='following-sibling::tr[1]//span[@class="score"]',
                            key='score',
                            data_type='text'
                        ),
                        BaseStep(
                            id='get_author',
                            action='data',
                            object_type='xpath',
                            object='following-sibling::tr[1]//a[@class="hnuser"]',
                            key='author',
                            data_type='text'
                        ),
                        BaseStep(
                            id='get_comments',
                            action='data',
                            object_type='xpath',
                            object='following-sibling::tr[1]//a[contains(text(), "comment")]',
                            key='comments',
                            data_type='text'
                        )
                    ]
                )
            ],
            pagination=PaginationConfig(
                strategy='next',
                nextButton=NextButtonConfig(
                    object_type='class',
                    object='morelink',
                    wait=2000
                ),
                maxPages=3
            )
        )
    ]

    try:
        print('🚀 Starting advanced scraper...')
        
        # Option 1: Get all results at once
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
        
        print('✅ Scraping completed!')
        print(f'📊 Found {len(results)} articles')
        print(json.dumps(results, indent=2))
        
        # Option 2: Stream results as they come (uncomment to use)
        """
        print('🚀 Starting streaming scraper...')
        
        async def on_result(result, index):
            print(f'📰 Article {index + 1}: {result.get("title")}')
            # JSON stringify the result
            print(json.dumps(result, indent=2))
        
        await run_scraper_with_callback(
            templates,
            on_result,
            RunOptions(
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
            )
        )
        
        print('✅ Streaming completed!')
        """
        
    except Exception as error:
        print(f'❌ Error: {error}')
        raise


# Run the example
if __name__ == '__main__':
    asyncio.run(advanced_example())

