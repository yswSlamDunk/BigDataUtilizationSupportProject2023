additionalColumns = ['preprocessedSentence', 'keyword', 'sentimentResult']
numTopics = [i for i in range(5, 21)]

config = {
    '19~23세 탈모': {
        'inputPath': '../Data/Raw/탈모톡톡_19~23세탈모.csv',
        'outputPath': '../Data/Preprocessed/탈모톡톡_19~23세탈모.csv',
        'needTitleContentCombine': True,
        'additionalColumns': ['titleContent'] + additionalColumns

    },

    '탈모수다': {
        'inputPath': '../Data/Raw/탈모톡톡_탈모수다.csv',
        'outputPath': '../Data/Preprocessed/탈모톡톡_탈모수다.csv',
        'needTitleContentCombine': True,
        'additionalColumns': ['titleContent'] + additionalColumns
    },

    '샴푸&영양제': {
        'inputPath': '../Data/Raw/샴푸&두피케어_샴푸&영양제.csv',
        'outputPath': '../Data/Preprocessed/샴푸&두피케어_샴푸&영양제.csv',
        'needTitleContentCombine': True,
        'additionalColumns': ['titleContent'] + additionalColumns
    },

    '샴푸&두피제품 찾기': {
        'inputPath': '../Data/Raw/샴푸&두피케어_샴푸&두피제품 찾기.csv',
        'outputPath': '../Data/Preprocessed/샴푸&두피케어_샴푸&두피제품 찾기.csv',
        'needTitleContentCombine': False,
        'additionalColumns': additionalColumns,
        'preprocessingColumns': ['commentContent', 'commentGood', 'commentBad'],
        'fillnaColumns': ['href','title','reviewNum', 'tag', 'brand', 'company', 'howToUse', 'ingredients', 'image', 'volume', 'price']
    },
}

ldaConfig = {
    '19~23세 탈모': {
        'inputPath': '../Data/Preprocessed/탈모톡톡_19~23세탈모.xlsx',
        'outputPath':'../Result/LDA/탈모톡톡_19~23세탈모/',
        'keywordColumn': 'keyword',
        'numTopics': numTopics
    },

    '탈모수다': {
        'inputPath': '../Data/Preprocessed/탈모톡톡_탈모수다.xlsx',
        'outputPath': '../Result/LDA/탈모톡톡_탈모수다/',
        'keywordColumn': 'keyword',
        'numTopics': numTopics
    },

    '샴푸&영양제': {
        'inputPath': '../Data/Preprocessed/샴푸&두피케어_샴푸&영양제.xlsx',
        'outputPath': '../Result/LDA/샴푸&두피케어_샴푸&영양제/',
        'keywordColumn': 'keyword',
        'numTopics': numTopics
    },

    '샴푸&두피제품 찾기':{
        'inputPath': '../Data/Preprocessed/샴푸&두피케어_샴푸&두피제품 찾기.xlsx',
        'outputPath': '../Result/LDA/샴푸&두피케어_샴푸&두피제품 찾기/',
        'keywordColumn': 'keyword',
        'numTopics': numTopics
    }
}

ldaAnalysisConfig = {
    
}