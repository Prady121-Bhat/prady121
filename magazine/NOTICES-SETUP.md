# Reader notices: how to open the box (owner's checklist)

Goal: readers send events, lost and found, road works, temple and school notices, shop openings, club and school results. You approve what is printed. The paper picks the approved ones up in the next morning's build (06:29 IST), so something sent by 8 pm the evening before can go in tomorrow's paper.

Nothing here costs money. Nothing is printed unless you type `yes` in the `approved` column.

## 1. Make the Google Form (5 minutes, on forms.google.com)

Questions, all "Short answer" unless noted:

| Question | Type | Required |
|---|---|---|
| Heading (for example "Lost: brown umbrella") | Short answer | yes |
| Details (what, where, time, who to call) | Paragraph | yes |
| Place (village or town) | Short answer | yes |
| Date of the event, or the first day it should appear | Date | yes |
| Last day it should appear (optional) | Date | no |
| Your name and phone number (for the editor only, never printed) | Short answer | no |

Do not make a question for the name or phone that the paper reads. The paper only reads heading, details, place and the dates.

Settings: turn off "Collect email addresses" if you do not want them. Copy the form link (Send, then the link icon). That is `form_url`.

## 2. Add the approval column

In the Form, open Responses, then "Link to Sheets" to create the response Sheet. In the Sheet, add one more column at the right and call it `approved`. For each row you accept, type `yes` in that column. Rows that stay empty are never printed.

## 3. Publish the Sheet as CSV

In the Sheet: File, Share, Publish to web. Choose the response sheet tab and the format "Comma-separated values (.csv)", then Publish. Copy the link. That is `sheet_csv_url`. Only the published copy is public, and you can stop publishing at any time from the same menu. The sheet itself stays private. Because the CSV is public, do not collect phone numbers in the same tab, or put them on a second tab that you do not publish.

## 4. Tell the paper

Fill `magazine/kullangal_config.json`:

```json
{
  "form_url": "https://forms.gle/...",
  "whatsapp_number": "919876543210",
  "sheet_csv_url": "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv"
}
```

`whatsapp_number` is optional (digits only, with country code). With it, a "Send on WhatsApp" button prefilled with a template appears; messages sent that way are typed into the Sheet or into `kullangal_notices.json` by hand.

## 5. Let the daily routine reach the Sheet

The daily routine runs in a cloud environment with a network allow-list. Add `docs.google.com` to the routine's environment network settings, and make sure the routine has the repository `Prady121-Bhat/prady121` attached as its source.

## Every day

1. Open the Sheet, read the new rows, type `yes` on those that may print, and fix typos in the Heading and Details cells.
2. Do it before the morning build (06:29 IST). Rows approved after that appear the next day.
3. A notice shows from its date until its last day (or only that day if no last day is given).

Until `form_url` or `whatsapp_number` is filled in, the Coast & Local page says reader notices are not open yet.
