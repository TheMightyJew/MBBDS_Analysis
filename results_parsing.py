import pandas as pd

file = open("results_28-04-2020_17-26-35.txt", "r")
cols = ['Number Of Pancakes', 'Gap', 'Problem ID', 'Start state', 'Goal state', 'Initial Heuristic'
                            , 'Algorithm', 'Memory', 'Status', 'States Expanded', 'Runtime(seconds)']
resultsDF = pd.DataFrame()
resDict = dict.fromkeys(cols)
gapStr = 'GAP-0'
resDict['Problem ID'] = 0
for line in file:
    line = line.replace('\t', '').replace('\n', '')
    splittedLine = line.replace(gapStr,' ' + gapStr + ' ').split()
    if 'TestPancakeHard' in line:
        resDict['Number Of Pancakes'] = int(splittedLine[splittedLine.index('TestPancakeHard:(Pancakes:')+1].replace(',', ''))
        resDict['Gap'] = int(splittedLine[splittedLine.index('Gap:')+1].replace(')', ''))
        gapStr = 'GAP-' + str(resDict['Gap'])
    elif 'Problem' in line:
        problemID = int(splittedLine[splittedLine.index('Problem')+1])
        if problemID > resDict['Problem ID']:
            resDict['Problem ID'] = problemID
        line = next(file).replace('\t', '').replace('\n', '')
        resDict['Start state'] = line[line.index(':')+1:-1]
        line = next(file).replace('\t', '').replace('\n', '')
        resDict['Goal state'] = line[line.index(':')+1:-1]
        line = next(file).replace('\t', '').replace('\n', '')
        resDict['Initial Heuristic'] = float(line[line.index('heuristic')+len('heuristic')+1:])
    elif gapStr in line:
        resDict['Algorithm'] = splittedLine[splittedLine.index(gapStr)+1]
        if 'memory' in line:
            if 'MBBDS' in resDict['Algorithm']:
                memoryStr = 'Memory_percentage_from_MM='
                resDict['Memory'] = int(splittedLine[splittedLine.index('memory')+2])
                resDict['Algorithm'] += '(' + line[line.index(memoryStr) + len(memoryStr):][:4] + ')'
            else:
                resDict['Memory'] = float(splittedLine[splittedLine.index('using')+1])
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

resultsDF[cols].to_csv('results.csv')

analysisCols = ['Gap', 'Algorithm', 'Failed', 'Mean Expansions', 'Mean Runtime']
analysisDF = pd.DataFrame()
analysisDict = dict.fromkeys(analysisCols)
import numpy as np
MBBDSFailSum = False
for gap in resultsDF['Gap'].unique():
        for algo in resultsDF['Algorithm'].unique():
            analysisDict['Gap'] = gap
            analysisDict['Algorithm'] = algo
            gapRows = (resultsDF['Gap'] == gap)
            algoRows = (resultsDF['Algorithm'] == algo)
            finishedRows = (resultsDF['Status'] == 1)
            if MBBDSFailSum and 'MBBDS' in algo:
                analysisDict['Failed'] += len(resultsDF[gapRows & algoRows & (resultsDF['Status'] == 0)])
            else:
                analysisDict['Failed'] = len(resultsDF[gapRows & algoRows & (resultsDF['Status'] == 0)])
            analysisDict['Mean Expansions'] = np.mean(resultsDF[gapRows & algoRows & finishedRows]['States Expanded'])
            analysisDict['Mean Runtime'] = np.mean(resultsDF[gapRows & algoRows & finishedRows]['Runtime(seconds)'])
            analysisDF = analysisDF.append(analysisDict, ignore_index=True)
            if 'MBBDS' in algo:
                MBBDSFailSum = True
            else:
                MBBDSFailSum = False


analysisDF[analysisCols].to_csv('analysis.csv')
