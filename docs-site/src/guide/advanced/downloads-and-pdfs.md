# Downloads & PDFs

Web scraping is not always about extracting text. Frequently, you need to capture visual proofs (screenshots), generate formal reports (PDFs), or trigger file downloads (CSVs, MP4s, ZIPs) hosted on the site.

StepWright provides simple, one-line actions for handling Playwright's download and printing APIs.

---

## 📸 Capturing Screenshots

### Full Page Storage
To grab the entire rendered DOM (even parts currently off-screen), use the `screenshot` action with `data_type="full"`.
```python
BaseStep(
    id="full_capture",
    action="screenshot",
    value="./storage/evidence.png",  # Relative or absolute Filepath destination
    data_type="full"                 # Required flag for full page
)
```

### Element-Level Storage
You can perfectly crop an image to a specific DOM element, like a chart, a specific tweet, or an invoice table:
```python
BaseStep(
    id="chart_capture",
    action="screenshot",
    object_type="id",
    object="quarterly-earnings-chart",
    value="./storage/chart.png"
)
```

---

## 🖨️ Generating PDF Documents

If you are scraping receipts, financial statements, or long articles, saving the result as a PDF is often cleaner than a rasterized image screenshot. 

> [!WARNING]
> PDF generation inside Python Playwright instances **strictly requires** the browser to be running in `headless=True` mode. You will receive an error if you attempt to use these actions while watching the browser visually.

### `savePDF` (Standard Method)
Generates a straightforward PDF representation of the current page.
```python
BaseStep(
    id="print_invoice",
    action="savePDF",
    value="./invoices/july_invoice.pdf"
)
```

### `printToPDF` (Styling Method)
This action forces the browser to apply CSS `@media print` rules before rendering. Use this if the target website strips out ads and navigation bars specifically for printing.
```python
BaseStep(
    id="print_clean",
    action="printToPDF",
    value="./invoices/july_invoice_clean.pdf"
)
```

---

## 📥 Intercepting Downloads

When you click an `<a>` tag or a button that forces the browser to download a file natively, traditional scrapers lose track of the binary blob. StepWright explicitly waits for the download event and reroutes the file to your disk.

### `eventBaseDownload`
This requires two pieces: the selector to click, and the file destination.

```python
BaseStep(
    id="download_report",
    action="eventBaseDownload",      # Tell the engine a download is expected
    object_type="id",
    object="export-csv-btn",         # The button that starts the download
    value="./downloads/export.csv"   # Where to save the intercepted payload
)
```

If you do not know the exact file name or extension beforehand (e.g., the server generates a random string), omit the explicit filename in the `value` param and just provide a directory path. Playwright will use the suggested filename from the server's `Content-Disposition` headers.

```python
BaseStep(
    id="download_dynamic",
    action="eventBaseDownload",      
    object_type="class",
    object="dl-file",         
    value="./downloads/"             # Wait, intercept, and save with the server's name 
)
```
