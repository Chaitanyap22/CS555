from datetime import datetime  # US08
import pandas as pd
import datetime
import dateutil.relativedelta
from tabulate import tabulate
from pandas._libs.tslibs.offsets import relativedelta

justLines = []
dictIndi = {}
dictFam = {}
with open('./Sprint 1/Family.ged') as f:
    lines = f.read().splitlines()
    justLines.append(lines)
lines = [[el] for el in lines]
for i in range(len(lines)):
    if((len(lines[i][0].strip().split())) < 2):
        lines[i] = "Incomplete GEDCOM on Line "+str(i)
    else:
        lines[i] = lines[i][0].strip().split(" ", 2)
        if(len(lines[i]) > 2 and lines[i][1] in ['INDI', 'FAM']):
            lines[i] = "Invalid GEDCOM on Line "+str(i)
        elif(len(lines[i]) > 2 and lines[i][2] in ['INDI', 'FAM']):
            lines[i][1], lines[i][2] = lines[i][2], lines[i][1]

valid_tags = {'INDI': '0', 'NAME': '1', 'SEX': '1', 'BIRT': '1', 'DEAT': '1', 'FAMC': '1', 'FAMS': '1', 'FAM': '0',
              'MARR': '1', 'HUSB': '1', 'WIFE': '1', 'CHIL': '1', 'DIV': '1', 'DATE': '2', 'HEAD': '0',
              'TRLR': '0', 'NOTE': '0'}

gedcom_out = []
for i in range(len(lines)):

    # print("-->"+justLines[0][i])
    if(len(lines[i]) > 2):
        if(lines[i][1] in valid_tags.keys() and valid_tags[lines[i][1]] == (lines[i][0])):
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|Y|"+lines[i][2])
            gedcom_out.append((lines[i][0], lines[i][1], lines[i][2]))
        elif(lines[i][0:2] == "In"):
            # print("<--"+lines[i])
            gedcom_out.append(lines[i])
        else:
            continue
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|N|"+lines[i][2])
    elif(len(lines[i]) == 2):
        if(lines[i][1] in valid_tags.keys() and valid_tags[lines[i][1]] == (lines[i][0])):
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|Y|")
            gedcom_out.append((lines[i][0], lines[i][1]))
        else:
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|N|")
            continue
gedcom_out.pop(0)
gedcom_out.pop(-1)
gedcom_out = list(filter((('1', 'BIRT')).__ne__, gedcom_out))

flag = 0
for i in range(len(gedcom_out)):
    if(i > 500):
        break
    lst_vals = []
    j = i+1
    if(gedcom_out[i][1] == 'INDI' and gedcom_out[i][0] == '0'):
        while(gedcom_out[j][1] != 'INDI'):
            key = gedcom_out[i][2][1:-1]
            if(gedcom_out[j][1] == 'FAM' and gedcom_out[j][0] == '0'):
                flag = 1
                break
            elif(gedcom_out[j][1] == 'DEAT' and gedcom_out[j][2] == 'Y'):
                lst_vals.append(('DEAT', gedcom_out[j+1][2]))
                j += 1
            elif(gedcom_out[j][1] == 'FAMS' or gedcom_out[j][1] == 'FAMC'):
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2][1:-1]))
            else:
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2]))
            j += 1
        dictIndi.update({key: lst_vals})
        if(flag == 1):
            break

# individuals dataframe
df_indi = pd.DataFrame(columns=[
                       'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouce'])
name, gender, birt, deat = "", "", "", ""
alive = False
for key, value in dictIndi.items():
    age = 0
    for i in range(len(value)):
        famc, fams = "", ""
        if(value[i][0] == 'NAME'):
            name = value[i][1]
        if(value[i][0] == 'SEX'):
            gender = value[i][1]
        if(value[i][0] == 'DATE'):
            birt = value[i][1]
            birt = datetime.datetime.strptime(birt, '%d %b %Y').date()
        if(value[i][0] == 'DEAT'):
            deat = value[i][1]
            deat = datetime.datetime.strptime(deat, '%d %b %Y').date()
        if(value[i][0] == 'FAMC'):
            famc = value[i][1]
        if(value[i][0] == 'FAMS'):
            fams = value[i][1]
    if (any('DEAT' in i for i in value)):
        alive = True
        age = relativedelta(deat, birt).years
    else:
        age = relativedelta(datetime.datetime.now(), birt).years

    df_indi = df_indi.append({'ID': key, 'Name': name, 'Gender': gender, 'Birthday': birt,
                              'Alive': alive, 'Death': deat, 'Child': famc, 'Spouce': fams, 'Age': age}, ignore_index=True)
    df_indi = (df_indi.replace(r'^\s*$', 'NA', regex=True))

flag = 0
for i in range(len(gedcom_out)):
    if(i > 1000):
        break
    lst_vals = []
    j = i+1
    if(gedcom_out[i][1] == 'FAM' and gedcom_out[i][0] == '0'):
        while(j < len(gedcom_out)):
            key = gedcom_out[i][2][1:-1]
            # husb wife child extract
            if(gedcom_out[j][1] != 'MARR' and gedcom_out[j][1] != 'DIV' and gedcom_out[j][1] != 'DATE' and gedcom_out[j][1] != 'FAM'):
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2][1:-1]))
            # married date extract
            elif(gedcom_out[j][1] == 'MARR' and len(gedcom_out[j+1]) > 2):
                lst_vals.append(('MARR', gedcom_out[j+1][2]))
            # divo date extract
            elif(gedcom_out[j][1] == 'DIV' and len(gedcom_out[j+1]) > 2):
                lst_vals.append(('DIV', gedcom_out[j+1][2]))
            # if next fam then break
            elif(gedcom_out[j][1] == 'FAM' and gedcom_out[j][0] == '0'):
                flag = 1
                break
            j += 1
        dictFam.update({key: lst_vals})

# Families dataframe
husb_id, wife_id = 0, 0
husb_name, wife_name = "", ""
child = []
df_fam = pd.DataFrame(columns=['ID', 'Married', 'Divorced',
                               'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'])
for key, value in dictFam.items():
    child = []
    married, div = "", ""
    for i in range(len(value)):
        if(value[i][0] == 'HUSB'):
            husb_id = value[i][1]
            husb_name = dictIndi[husb_id][0][1]
        if(value[i][0] == 'WIFE'):
            wife_id = value[i][1]
            wife_name = dictIndi[wife_id][0][1]
        if(value[i][0] == 'CHIL'):
            child.append(value[i][1])
        if(value[i][0] == 'MARR'):
            married = value[i][1]
            married = datetime.datetime.strptime(married, '%d %b %Y').date()
        if(value[i][0] == 'DIV'):
            div = value[i][1]
            div = datetime.datetime.strptime(div, '%d %b %Y').date()

    df_fam = df_fam.append({'ID': key, 'Married': married, 'Divorced': div, 'Husband ID': husb_id,
                            'Husband Name': husb_name, 'Wife ID': wife_id, 'Wife Name': wife_name, 'Children': child, }, ignore_index=True)
    df_fam = (df_fam.replace(r'^\s*$', 'NA', regex=True))

print("Individuals")
print(tabulate(df_indi, headers='keys', tablefmt='psql'))
print("Families")
print(tabulate(df_fam, headers='keys', tablefmt='psql'))
print('\n\n')

##########__________________Vedadnya's Code__________________########################

# User Story 03 : VJ
# Birth before Death


def us03():
    df_copy = df_indi.copy()
    todayDate = datetime.datetime.today().strftime('%Y-%m-%d')
    todayDate = datetime.datetime.strptime(todayDate, '%Y-%m-%d').date()
    df_copy = df_copy.replace({'Death': 'NA'}, todayDate)

    correct = []
    error = []

    for i, j in df_copy.iterrows():
        if df_copy['Death'][i] > df_copy['Birthday'][i]:
            correct.append("CORRECT: " + "INDIVIDUAL: " + "US03: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + df_copy['Name'][i] + " has a correct Birthdate: " + str(
                df_copy['Birthday'][i]) + " with respect to Deathdate: " + str(df_copy['Death'][i]))
        else:
            error.append("ERROR: " + "INDIVIDUAL: " + "US03: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + df_copy['Name'][i] + " has a future Birthdate: " + str(
                df_copy['Birthday'][i]) + " with respect to Deathdate: " + str(df_copy['Death'][i]))
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US01: No records found')
        return(error)


#print("\n\n\nUser story 03 output:\n\n")
us03Error = us03()
print(*us03Error, sep="\n")

# User Story 04 : VJ
# Marriage before Divorce


def us04():
    df_copy = df_fam.copy()
    correct = []
    error = []
    for i, j in df_copy.iterrows():
        if df_copy['Divorced'][i] == 'NA' or df_copy['Married'][i] == 'NA':
            continue
        if df_copy['Divorced'][i] > df_copy['Married'][i]:
            correct.append("CORRECT: " + "FAMILY: " + "US04: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + " have a correct Marriage Date : " + str(
                df_copy['Married'][i]) + " with respect to Divorced Date : " + str(df_copy['Divorced'][i]))
        else:
            error.append("ERROR: " + "FAMILY: " + "US04: " + str(i) + ": " + " " + df_copy['ID'][i] + ": " + " have a future Marriage Date : " + str(
                df_copy['Married'][i]) + " with respect to Divorced Date : " + str(df_copy['Divorced'][i]))
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US01: No records found')
        return(error)


#print("\n\n\nUser story 04 output:\n\n")
us04Error = us04()
print(*us04Error, sep="\n")


##########__________________Pranav's Code__________________########################


# User Story 05: Marriage before death
def us_05_marriage_before_death():

    df_copy = df_indi.copy()
    #todayDate = datetime.datetime.today().strftime('%Y-%m-%d')
    todayDate = datetime.datetime.strptime('2020-04-01', '%Y-%m-%d').date()
    #todayDate = datetime.datetime.strptime(todayDate, '%Y-%m-%d').date()
    df_copy = df_copy.replace({'Death': 'NA'}, todayDate)
    correct = []
    wrong = []

    df_us_05 = pd.DataFrame(columns=[
                            'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
    for index, col in df_fam.iterrows():
        husb_id = col["Husband ID"]
        marriage_date = col['Married']
        wife_id = col["Wife ID"]

        for index, col in df_copy.iterrows():
            # check if indi id matches with hus_id or wife_id
            if ((col["ID"] == husb_id) or (col["ID"] == wife_id)):
                # given condition if marriage exists, death exists
                if ((marriage_date != "NA") and (col["Death"] > marriage_date)):
                    df_us_05 = df_us_05.append(col)

    error = pd.concat([df_us_05, df_copy],
                      sort=False).drop_duplicates(keep=False)
    df_us_05['Outcome'] = True
    error['Outcome'] = False

    result = df_us_05.append(error, ignore_index=True)
    result = result.sort_values(by=['ID'], ascending=True)
    # print("\n")
    for i, j in result.iterrows():
        if j["Outcome"] is True:
            correct.append("CORRECT: " + "INDIVIDUAL: " + "US05: " + str(i) + ": " + " " +
                           j['ID'] + ": " + j['Name'] + " has a correct Marriage Date with respect to Deathdate: " + str(j['Death']))

        else:
            wrong.append("ERROR: " + "INDIVIDUAL: " + "US05: " + str(i) + ": " + " " +
                         j['ID'] + ": " + j['Name'] + " has an erroneous Marriage Date with respect to Deathdate: " + str(j['Death']))

    if((len(wrong)) > 0):
        return (wrong)
    else:
        wrong.append('ERROR: US01: No records found')
        return(wrong)


#print("\n\nUSER STORY 05 TEST :")
us05Error = us_05_marriage_before_death()
print(*us05Error, sep="\n")
# print('\n')

# User Story 06: divorce before death


def us_06_divorce_before_death():

    df_copy = df_indi.copy()
    #todayDate = datetime.datetime.today().strftime('%Y-%m-%d')
    todayDate = datetime.datetime.strptime('2020-04-01', '%Y-%m-%d').date()
    #todayDate = datetime.datetime.strptime(todayDate, '%Y-%m-%d').date()
    df_copy = df_copy.replace({'Death': 'NA'}, todayDate)
    correct = []
    wrong = []
    df_us_06 = pd.DataFrame(columns=[
                            'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouse'])
    for index, col in df_fam.iterrows():
        husb_id = col["Husband ID"]
        divorce_date = col['Divorced']
        marriage_date = col['Married']
        wife_id = col["Wife ID"]

        for index, col in df_copy.iterrows():
            # check if indi id matches with hus_id or wife_id
            if ((col["ID"] == husb_id) or (col["ID"] == wife_id)):
                # given condition if divorce exists, death exists
                if ((divorce_date != "NA") and (marriage_date != "NA") and (col["Death"] > divorce_date)):
                    df_us_06 = df_us_06.append(col)

    error = pd.concat([df_us_06, df_copy],
                      sort=False).drop_duplicates(keep=False)
    df_us_06['Outcome'] = True
    error['Outcome'] = False

    result = df_us_06.append(error, ignore_index=True)
    result = result.sort_values(by=['ID'], ascending=True)
    # print("\n")
    for i, j in result.iterrows():
        if j["Outcome"] is True:
            correct.append("CORRECT: " + "INDIVIDUAL: " + "US06: " + str(i) + ": " + " " +
                           j['ID'] + ": " + j['Name'] + " has a correct Divorce Date with respect to Deathdate: " + str(j['Death']))

        else:
            wrong.append("ERROR: " + "INDIVIDUAL: " + "US06: " + str(i) + ": " + " " +
                         j['ID'] + ": " + j['Name'] + " has an erroneous Divorce Date with respect to Deathdate: " + str(j['Death']))

    if((len(wrong)) > 0):
        return (wrong)
    else:
        wrong.append('ERROR: US01: No records found')
        return(wrong)


#print("\n\nUSER STORY 06 TEST :")
us06Error = us_06_divorce_before_death()
print(*us06Error, sep="\n")
# print('\n')

##########__________________Sanket's Code__________________########################

# US07 : SP
# Less then 150 years old


def US07():
    errors = []
    for i, c in df_indi.iterrows():
        if (df_indi['Age'][i] > 150):
            errors.append("ERROR: "+"INDIVIDUAL: "+"US07: "+str(i)+': '+c['ID']+": "+c['Name']+" is " +
                          str(c['Age'])+" years old which is more then 150")
            #print(*errors, sep="\n")
    if((len(errors)) > 0):
        return (errors)
    else:
        errors.append('ERROR: US01: No records found')
        return(errors)


#print("User story 07 output: \n")
errorUS07 = US07()
print(*errorUS07, sep="\n")
# print('\n')

# US08 : SP
# Birth before marriage of parents


def US08():
    errors = []
    for index, col in df_fam.iterrows():
        id = col['ID']
        marr = col['Married']
        child = col['Children']
        div = col['Divorced']
        for i, c in df_indi.iterrows():
            if(marr != 'NA'):
                if((c['Birthday'] < marr) and (c['ID'] in child)):
                    errors.append("ERROR: "+"FAMILY: "+"US08: "+str(i)+': '+c['ID']+": "+c['Name'] +
                                  " is born before marriage of parents")
            if(marr != 'NA' and div != 'NA'):
                check = div + dateutil.relativedelta.relativedelta(months=9)
                if((c['Birthday'] > check) and (c['ID'] in child)):
                    errors.append("ERROR: "+"FAMILY: "+"US08: "+str(i)+': ' +
                                  c['ID']+": "+c['Name']+" is born after 9 months from divorce of parents")
    if((len(errors)) > 0):
        return (errors)
    else:
        errors.append('ERROR: US01: No records found')
        return(errors)


#print("User story 08 output: \n")
errorUS08 = US08()
print(*errorUS08, sep="\n")
# print('\n')

#############__________________Parth's Code__________________###############

# US01 : PP
# Dates before current date


def US01():
    error = []
    todayDate = datetime.datetime.strptime(
        datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
    for i in range(len(df_indi)):
        if(df_indi['Birthday'][i] != 'NA' and df_indi['Birthday'][i] > todayDate):
            birthday = 'ERROR: INDIVIDUAL: US01: ' + \
                str(i)+': '+df_indi.loc[i]['ID']+': ' + str(df_indi.loc[i]['Name']) + ' has a Birthday on ' + \
                str(df_indi.loc[i]['Birthday']) + ' which occurs in the future'
            error.append(birthday)
        elif(df_indi['Death'][i] != 'NA' and df_indi['Death'][i] > todayDate):
            deathdate = 'ERROR: INDIVIDUAL: US01: ' + \
                str(i)+': '+df_indi.loc[i]['ID']+': ' + str(df_indi.loc[i]['Name']) + ' has a Deathday on ' + \
                str(df_indi.loc[i]['Death']) + ' which occurs in the future'
            error.append(deathdate)
    for i in range(len(df_fam)):
        if(df_fam['Married'][i] != 'NA' and df_fam['Married'][i] > todayDate):
            married = 'ERROR: FAMILY: US01: '+str(i)+': '+df_fam.loc[i]['ID']+': '+'Marriage Day ' + str(
                df_fam.loc[i]['Married']) + ' between ' + df_fam.loc[i]['Husband Name']+' (ID: ' + df_fam.loc[i]['Husband ID']+')'+' and ' + df_fam.loc[i]['Wife Name'] + ' (ID: '+df_fam.loc[i]['Wife ID'] + ')' + ' occurs in the future'
            error.append(married)
        elif(df_fam['Divorced'][i] != 'NA' and df_fam['Divorced'][i] > todayDate):
            divorced = 'ERROR: FAMILY: US01: '+str(i)+': '+df_fam.loc[i]['ID']+': '+'Divorce Day ' + str(
                df_fam.loc[i]['Divorced']) + ' between ' + df_fam.loc[i]['Husband Name']+' (ID: ' + df_fam.loc[i]['Husband ID']+')'+' and ' + df_fam.loc[i]['Wife Name'] + ' (ID: '+df_fam.loc[i]['Wife ID'] + ')' + ' occurs in the future'
            error.append(divorced)
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US01: No records found')
        return(error)


errorUS01 = US01()
print(*errorUS01, sep="\n")

# US02 : PP
# Dates Birth before marriage


def US02():
    error = []
    for i in range(len(df_indi)):
        if(df_indi['Birthday'][i] != 'NA' and df_indi['Spouce'][i] != 'NA' and (df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) < (df_indi['Birthday'][i])):
            if(df_indi['Gender'][i] == 'M'):
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a birthday on ' + str(
                    df_indi.loc[i]['Birthday']) + ' which is after his marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0])
                error.append(print_line)
            elif(df_indi['Gender'][i] == 'F'):
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a birthday on ' + str(
                    df_indi.loc[i]['Birthday']) + ' which is after her marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0])
                error.append(print_line)
            else:
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a birthday on ' + str(
                    df_indi.loc[i]['Birthday']) + ' which is after their marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) + '\n'
                error.append(print_line)
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US01: No records found')
        return(error)


errorUS02 = US02()
print(*errorUS02, sep="\n")