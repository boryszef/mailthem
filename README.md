# mailThem.py

This is a small Python script created to send an announcement about
a conference (MDMM2018) to the participants of the previous editions.
Supports TLS encryption.

List of emails should be provided in `emails.txt`.
The e-mail is sent both, as plain text and HTML (files `plain.txt`
and `rich.html`). At the top of the script there are some variables
that allow for customization. In particular, `dryRun = True` allows to
try the script without really sending the emails.
