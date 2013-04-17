#Python
#
#

location = r'/Users/tabulaw/Documents/workspace/uslaw/codeupdate/newlaws'

#sedfunction = r'/This\sAct\smay\sbe\scited/ {N; s_\n_ _; s_(This\sAct\smay\sbe\scited\sas\sthe)([^a-zA-Z]*)([a-zA-Z0-9 ]*)(.*\.)_\1\2<span class="cited-as-title">\3</span>\4_;}; ' 
sedfunction = r'/^S[Ee][Cc].\s\d+\./ {N; s_(^S[Ee][Cc].\s)(\d+\.)(.*\n?.*\.$)_</div><div class="section" id="SEC-\2"><span class="title">\1\2\3</span>_;}; '
sedfunction += r'/^SECTION\s1./ {s_(^SECTION\s1.)(.*)_<div class="section" id="SEC-1"><span class="title">\1\2</span>_;};'
sedfunction += r'/Approved\s\w*\s\d+,/ i\
</div>' 

