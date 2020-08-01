import pandas as pd
import numpy as np

filenames = ['old_rev', 'new_rev']
for filename in filenames:
    fileName = filename.replace('.txt', '')
    file = open(fileName + ".txt", "r")
    cols = ['Number Of Pancakes', 'Gap', 'Problem ID', 'Start state', 'Goal state', 'Initial Heuristic', 'Algorithm',
            'Memory', 'Status', 'States Expanded', 'Necessary Expansions', 'Iterations', 'Runtime(seconds)']
    errorCols = ['Number Of Pancakes', 'Gap', 'Problem ID', 'Algorithm', 'Memory', 'Status', 'solLength',
                 'realSolLength']
    resultsDF = pd.DataFrame()
    errorsDF = pd.DataFrame()
    resDict = dict.fromkeys(cols)
    errorsDict = dict.fromkeys(errorCols)
    gapStr = 'GAP-0'
    resDict['Problem ID'] = 0
    errorsDict['Problem ID'] = 0
    necessary = 0
    for line in file:
        isError = False
        line = line.replace('\t', '').replace('\n', '')
        splittedLine = line.replace(gapStr, ' ' + gapStr + ' ').split()
        if 'TestPancake' in line:
            resDict['Number Of Pancakes'] = int(
                splittedLine[splittedLine.index('TestPancake:(Pancakes:') + 1].replace(',', ''))
            resDict['Gap'] = int(splittedLine[splittedLine.index('Gap:') + 1].replace(')', '').replace(',', ''))
            gapStr = 'GAP-' + str(resDict['Gap'])
        elif 'Problem' in line:
            problemID = int(splittedLine[splittedLine.index('Problem') + 1])
            MMsolLength = 0
            AsolLength = 0
            solLength = 0
            realSolLength = 0
            resDict['Problem ID'] = problemID
            line = next(file).replace('\t', '').replace('\n', '')
            resDict['Start state'] = line[line.index(':') + 1:-1]
            line = next(file).replace('\t', '').replace('\n', '')
            resDict['Goal state'] = line[line.index(':') + 1:-1]
            line = next(file).replace('\t', '').replace('\n', '')
            resDict['Initial Heuristic'] = float(line[line.index('heuristic') + len('heuristic') + 1:])
        else:
            if line[0] == line[-1] == '_' or 'completed' in line:
                continue
            resDict['Algorithm'] = splittedLine[0]
            if 'necessary' in line:
                necessary = int(splittedLine[splittedLine.index('necessary;') - 1])
            resDict['Necessary Expansions'] = necessary
            if 'MBBDS' in resDict['Algorithm']:
                resDict['Iterations'] = int(splittedLine[splittedLine.index('iterations;') - 1])
            else:
                resDict['Iterations'] = 0
            if 'MM found' in line:
                MMsolLength = float(splittedLine[splittedLine.index('length') + 1].replace(';', ''))
            if 'A* found' in line:
                AsolLength = float(splittedLine[splittedLine.index('length') + 1].replace(';', ''))
            if 'memory' in line:
                if 'MBBDS' in resDict['Algorithm'] or '+' in resDict['Algorithm']:
                    memoryStr = 'Memory_Percentage='
                    resDict['Memory'] = int(splittedLine[splittedLine.index('memory') + 2])
                    resDict['Algorithm'] += '(' + line[line.index(memoryStr) + len(memoryStr):][:4] + ')'
                    if 'length' in line:
                        algos2Check = ['MBBDS', 'A*+IDA*(', 'A*+IDA*_Reverse(', 'MM+IDMM', 'A*+IDMM']
                        for algo2Check in algos2Check:
                            if algo2Check in resDict['Algorithm']:
                                solLength = float(splittedLine[splittedLine.index('length') + 1].replace(';', ''))
                                realSolLength = max(AsolLength, MMsolLength)
                                if solLength not in [AsolLength, MMsolLength]:
                                    isError = True
                                    break
                else:
                    resDict['Memory'] = float(splittedLine[splittedLine.index('using') + 1])
            else:
                resDict['Memory'] = '-'
            if 'fail' in line:
                resDict['Status'] = 0
                resDict['States Expanded'] = '-'
                resDict['Runtime(seconds)'] = '-'
            else:
                resDict['Status'] = 1
                try:
                    resDict['States Expanded'] = int(splittedLine[splittedLine.index('expanded;') - 1])
                except:
                    print(line)
                if 'elapsed' in splittedLine:
                    resDict['Runtime(seconds)'] = float(
                        splittedLine[splittedLine.index('elapsed') - 1].replace('s', ''))
                elif 'elapsed;' in splittedLine:
                    resDict['Runtime(seconds)'] = float(
                        splittedLine[splittedLine.index('elapsed;') - 1].replace('s', ''))
            resultsDF = resultsDF.append(resDict, ignore_index=True)
            if isError:
                algoName = resDict['Algorithm']
                if '(' in algoName:
                    algoName = algoName[:algoName.index('(')]
                errorsDict = {'Number Of Pancakes': resDict['Number Of Pancakes'], 'Gap': resDict['Gap'],
                              'Problem ID': resDict['Problem ID'], 'Algorithm': algoName, 'Memory': resDict['Memory'],
                              'Status': resDict['Status'],
                              'solLength': solLength,
                              'realSolLength': realSolLength}
                errorsDF = errorsDF.append(errorsDict, ignore_index=True)

    resultsDF = resultsDF[cols]
    resultsDF.to_csv(fileName + '_results.csv')
    errorsDF.drop_duplicates(inplace=True)
    if len(errorsDF) > 0:
        errorsDF.sort_values(['Number Of Pancakes', 'Gap', 'Problem ID', 'Algorithm', 'Memory'], ascending=True,
                             inplace=True)
        errorsDF = errorsDF[errorCols]
    errorsDF.to_csv(fileName + '_errors.csv')

    analysisCols = ['Gap', 'Algorithm', 'Failed(Out Of 100)', 'Mean Expansions', 'Mean Necessary Expansions',
                    'Mean Iterations', 'Mean Runtime(Seconds)']
    analysisDF = pd.DataFrame()
    analysisDict = dict.fromkeys(analysisCols)
    MBBDSFailSum = None
    failedRows = (resultsDF['Status'] == 0)
    for gap in resultsDF['Gap'].unique():
        analysisDict['Gap'] = gap
        gapRows = (resultsDF['Gap'] == gap)
        finished_problems_Rows = (resultsDF['Problem ID'].isin(
            set(resultsDF[gapRows]['Problem ID']) - set(resultsDF[gapRows & (failedRows)]['Problem ID'])))
        for algo in resultsDF['Algorithm'].unique():
            analysisDict['Algorithm'] = algo
            algoRows = (resultsDF['Algorithm'] == algo)
            if MBBDSFailSum == algo:
                analysisDict['Failed(Out Of 100)'] += len(resultsDF[gapRows & algoRows & failedRows])
            else:
                analysisDict['Failed(Out Of 100)'] = len(resultsDF[gapRows & algoRows & failedRows])
            analysisDict['Mean Expansions'] = int(
                np.mean(resultsDF[gapRows & algoRows & finished_problems_Rows]['States Expanded']))
            analysisDict['Mean Necessary Expansions'] = int(
                np.mean(resultsDF[gapRows & algoRows & finished_problems_Rows]['Necessary Expansions']))
            analysisDict['Mean Iterations'] = int(
                np.mean(resultsDF[gapRows & algoRows & finished_problems_Rows]['Iterations']))
            analysisDict['Mean Runtime(Seconds)'] = round(
                np.mean(resultsDF[gapRows & algoRows & finished_problems_Rows]['Runtime(seconds)']), 3)
            analysisDF = analysisDF.append(analysisDict, ignore_index=True)
            MBBDSFailSum = algo

    analysisDF[analysisCols].to_csv(fileName + '_analysis.csv')
