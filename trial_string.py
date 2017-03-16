license = "License: \n20-113047 (Validity: 04/02/2020) \n20C-113049 (Validity: 04/02/2020) \n21-113048 (Validity: 04/02/2020)"
lic_no = license.split('\n')
for lic in lic_no:
  if "License:" not in lic:
    lic_details = lic.split(' ')
    lic_details_x = lic_details[2].split(')')
    print lic_details[0] + " and " + lic_details_x[0]
