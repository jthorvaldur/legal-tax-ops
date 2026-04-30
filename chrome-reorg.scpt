-- Chrome Tab Reorganizer
-- Closes all windows, then opens tabs grouped into named windows

tell application "Google Chrome"
	-- Close all existing windows
	close every window
	delay 1

	-- GROUP 1: Case Filing (Cook County)
	make new window
	set w1 to window 1
	set URL of active tab of w1 to "https://jthorvaldur.github.io/r/cook6724-QgixOl/filing/"

	tell w1
		make new tab with properties {URL:"https://jthorvaldur.github.io/r/cook6724-QgixOl/filing/roadmap.html"}
		make new tab with properties {URL:"https://jthorvaldur.github.io/r/cook6724-QgixOl/filing/legal_guide.html"}
		make new tab with properties {URL:"https://jthorvaldur.github.io/r/cook6724-QgixOl/filing/legal_guide.html#foundations"}
		make new tab with properties {URL:"https://jthorvaldur.github.io/r/cook6724-QgixOl/filing/strategy.html"}
		make new tab with properties {URL:"file:///Users/jthor/div_legal/reports/case_timeline.html"}
		make new tab with properties {URL:"https://efileil.tylertech.cloud/OfsEfsp/ui/dashboard"}
		make new tab with properties {URL:"https://efileil.tylertech.cloud/OfsEfsp/ui/edit-envelope/48bb9876-79db-4f45-8909-20362d04c6eb/filings"}
		make new tab with properties {URL:"https://efile.illinoiscourts.gov/"}
		make new tab with properties {URL:"https://efile.illinoiscourts.gov/EFSPs-Page/"}
		make new tab with properties {URL:"https://efile.illinoiscourts.gov/self-represented-filers-page/"}
	end tell

	-- GROUP 2: Scripture Research
	make new window
	set w2 to window 1
	set URL of active tab of w2 to "https://biblehub.com/text/psalms/144-1.htm"

	tell w2
		make new tab with properties {URL:"https://www.biblegateway.com/passage/?search=Psalm%20144-150&version=NKJV"}
		make new tab with properties {URL:"https://www.bible.com/bible/316/PSA.144.TS2009"}
		make new tab with properties {URL:"https://en.wikipedia.org/wiki/Psalm_144"}
		make new tab with properties {URL:"https://en.wikipedia.org/wiki/Tetragrammaton"}
	end tell

	-- GROUP 3: Personal Site / GitHub
	make new window
	set w3 to window 1
	set URL of active tab of w3 to "https://jthorvaldur.github.io/"

	tell w3
		make new tab with properties {URL:"https://jthorvaldur.github.io/r/"}
		make new tab with properties {URL:"https://github.com/jthorvaldur/jthorvaldur.github.io/tree/main"}
		make new tab with properties {URL:"https://github.com/jthorvaldur/jthorvaldur.github.io/blob/main/index.html"}
	end tell

	-- GROUP 4: LinkedIn Data Export
	make new window
	set w4 to window 1
	set URL of active tab of w4 to "https://www.linkedin.com/mypreferences/d/download-my-data"

	tell w4
		make new tab with properties {URL:"https://www.linkedin.com/help/linkedin/answer/a1339364/downloading-your-account-data"}
	end tell

	-- GROUP 5: Upwork Hiring
	make new window
	set w5 to window 1
	set URL of active tab of w5 to "https://www.upwork.com/ab/applicants/2042731759589949382/applicants?nav_dir=pop"

	tell w5
		make new tab with properties {URL:"https://www.upwork.com/ab/applicants/2042712999810334662/applicants"}
	end tell

end tell
