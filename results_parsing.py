import pandas as pd

fileName = 'pancakes'
file = open(fileName + ".txt", "r")
cols = ['Number Of Pancakes', 'Gap', 'Problem ID', 'Start state', 'Goal state', 'Initial Heuristic'
    , 'Algorithm', 'Memory', 'Status', 'States Expanded', 'Runtime(seconds)']
resultsDF = pd.DataFrame()
resDict = dict.fromkeys(cols)
gapStr = 'GAP-0'
resDict['Problem ID'] = 0
for line in file:
    line = line.replace('\t', '').replace('\n', '')
    splittedLine = line.replace(gapStr, ' ' + gapStr + ' ').split()
    if 'TestPancakeHard' in line:
        resDict['Number Of Pancakes'] = int(
            splittedLine[splittedLine.index('TestPancakeHard:(Pancakes:') + 1].replace(',', ''))
        resDict['Gap'] = int(splittedLine[splittedLine.index('Gap:') + 1].replace(')', ''))
        gapStr = 'GAP-' + str(resDict['Gap'])
    elif 'Problem' in line:
        problemID = int(splittedLine[splittedLine.index('Problem') + 1])
        resDict['Problem ID'] = problemID
        line = next(file).replace('\t', '').replace('\n', '')
        resDict['Start state'] = line[line.index(':') + 1:-1]
        line = next(file).replace('\t', '').replace('\n', '')
        resDict['Goal state'] = line[line.index(':') + 1:-1]
        line = next(file).replace('\t', '').replace('\n', '')
        resDict['Initial Heuristic'] = float(line[line.index('heuristic') + len('heuristic') + 1:])
    elif gapStr in line:
        resDict['Algorithm'] = splittedLine[splittedLine.index(gapStr) + 1]
        if 'memory' in line:
            if 'MBBDS' in resDict['Algorithm']:
                memoryStr = 'Memory_percentage_from_MM='
                resDict['Memory'] = int(splittedLine[splittedLine.index('memory') + 2])
                resDict['Algorithm'] += '(' + line[line.index(memoryStr) + len(memoryStr):][:4] + ')'
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
            resDict['States Expanded'] = int(splittedLine[splittedLine.index('expanded;') - 1])
            if 'elapsed' in splittedLine:
                resDict['Runtime(seconds)'] = float(splittedLine[splittedLine.index('elapsed') - 1].replace('s', ''))
            elif 'elapsed;' in splittedLine:
                resDict['Runtime(seconds)'] = float(splittedLine[splittedLine.index('elapsed;') - 1].replace('s', ''))
        resultsDF = resultsDF.append(resDict, ignore_index=True)
resultsDF = resultsDF[cols]
resultsDF.to_csv(fileName + '_results.csv')

analysisCols = ['Gap', 'Algorithm', 'Failed(Out Of 100)', 'Mean Expansions', 'Mean Runtime(Seconds)']
analysisDF = pd.DataFrame()
analysisDict = dict.fromkeys(analysisCols)
import numpy as np

MBBDSFailSum = False

failedRows = (resultsDF['Status'] == 0)
for gap in resultsDF['Gap'].unique():
    analysisDict['Gap'] = gap
    gapRows = (resultsDF['Gap'] == gap)
    finished_problems_Rows = (resultsDF['Problem ID'].isin(set(resultsDF[gapRows]['Problem ID'])-set(resultsDF[gapRows & (failedRows)]['Problem ID'])))
    for algo in resultsDF['Algorithm'].unique():
        analysisDict['Algorithm'] = algo
        algoRows = (resultsDF['Algorithm'] == algo)
        if MBBDSFailSum and 'MBBDS' in algo:
            analysisDict['Failed(Out Of 100)'] += len(resultsDF[gapRows & algoRows & failedRows])
        else:
            analysisDict['Failed(Out Of 100)'] = len(resultsDF[gapRows & algoRows & failedRows])
        analysisDict['Mean Expansions'] = int(np.mean(resultsDF[gapRows & algoRows & finished_problems_Rows]['States Expanded']))
        analysisDict['Mean Runtime(Seconds)'] = round(np.mean(resultsDF[gapRows & algoRows & finished_problems_Rows]['Runtime(seconds)']) ,3)
        analysisDF = analysisDF.append(analysisDict, ignore_index=True)
        if 'MBBDS' in algo:
            MBBDSFailSum = True
        else:
            MBBDSFailSum = False

analysisDF[analysisCols].to_csv(fileName + '_analysis.csv')
