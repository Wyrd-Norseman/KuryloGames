# kurylogames.uk: your new portfolio

The whole site is one file, `index.html`. No builder, no framework, no monthly fee for the site itself.

## Editing content

Open `index.html` and look for the block that starts with `<script id="site-data"`. All text, projects, image lists, links and the email address live there as plain JSON:

- **Add your email:** set `"email": "you@example.com"` under `settings`. It appears in the contact credits.
- **Edit a project:** each project has a `title`, `role`, `summary` (index line), `tagline` (the subtitle under its title), `facts`, `chapters` and a `gallery`.
- **Add a project:** copy an existing one, give it a new `slug` (that becomes its link, e.g. `kurylogames.uk/#my-new-game`).
- **Image layouts:** each figure group has a `layout` of `grid`, `wide`, `masonry` or `pair`. Add `diagram` (e.g. `"wide diagram"`) for sketches and charts so they aren't cropped.
- **Captions:** use `{ "k": "image-key", "c": "Caption text" }` instead of a plain image key.
- **Your own new images:** put them in an `images/` folder and use the path, e.g. `"images/koras/combat.jpg"`.

## Playable CV

`playable-cv.html` is your platformer CV. The CV link in the header, "Play my CV" on the About section and "Playable CV" in the contact credits all open it. Replace the file to update it. The PDF stays available as "Download my CV (PDF)".

## Videos

Show reels play silently on a loop at the top of a page, with a "Play with sound" button. Other videos sit lower down and only play when clicked.

- **Your own files live in `videos/`.** A page's top video is `"video": { "src": "videos/name.mp4", "poster": "videos/name.jpg" }`. The poster is the still shown while it loads. The home page uses `heroVideo` under `person`: a 27-second silent reel cut from your four show reels (`videos/home-reel.mp4`), so it has `"sound": false` and no sound button.
- **Click-to-play video in a section:** `{ "video": "videos/name.mp4", "poster": "videos/name.jpg", "c": "Caption" }` in any figure group.
- **YouTube instead of a file:** `"video": { "id": "YOUTUBE_ID", "start": 0 }` for a top video, or `{ "yt": "YOUTUBE_ID", "c": "Caption" }` in a section. The two full-length gameplay videos (Frank Stone and the Last Drop winter level) use YouTube because the originals are 2.4–2.6 GB. YouTube videos only play once the site is online, or via `python3 -m http.server` (open http://localhost:8000), not from a double-clicked file.
- **Adding more of your own:** keep them web-sized. 1080p H.264 MP4 at roughly 4–8 Mbps is plenty, and a show reel under about 20 MB starts quickly. GitHub Pages rejects any file over 100 MB.

Keep the JSON valid: double quotes, commas between items, no trailing comma. If the page goes blank after an edit, paste the block into jsonlint.com to find the typo.

## Before you leave Squarespace

Right now the images and your PDF CV still load from Squarespace's servers. Copy them into this folder first:

```
py -m pip install pillow
py fetch_assets.py
```

(On Mac/Linux use `python3` instead of `py`.) Pillow is optional but shrinks the screenshots to roughly a tenth of their size, which makes pages load much faster. The script saves everything into `images/`, downloads your CV, and switches the site to load it all locally. If anything fails, run it again; finished files are skipped.

## Putting it online (GitHub Pages)

1. Create a free GitHub account, then a new **public** repository (e.g. `kurylogames-site`).
2. Install **GitHub Desktop**, clone the empty repository, copy everything from this folder into it (including the hidden `.nojekyll` file), then **Commit** and **Push**. The browser upload won't take the larger videos, so use GitHub Desktop.
3. On GitHub: repository **Settings → Pages → Build and deployment**: Source "Deploy from a branch", branch `main`, folder `/ (root)`. Save. After a minute the site is live at `https://<username>.github.io/kurylogames-site/`. Check it there first.
4. Same page, **Custom domain**: enter `kurylogames.uk` and Save.
5. In Squarespace: **Domains → kurylogames.uk → DNS**. Delete the Squarespace Defaults records, then add:
   - `A` record, host `@`, value `185.199.108.153`
   - `A` record, host `@`, value `185.199.109.153`
   - `A` record, host `@`, value `185.199.110.153`
   - `A` record, host `@`, value `185.199.111.153`
   - `CNAME` record, host `www`, value `<username>.github.io`
6. Wait for DNS (minutes to a day). Back in GitHub Pages settings, tick **Enforce HTTPS** once it's offered.
7. Only once kurylogames.uk shows the new site: cancel the Squarespace **website** subscription. Keep the **domain** subscription, which is separate and keeps your address.

## Updating the site later

Edit the files, then Commit and Push in GitHub Desktop. The live site updates within a minute or two.
