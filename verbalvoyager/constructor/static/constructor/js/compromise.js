if (typeof nlp !== "function") {
	console.error("Compromise.js не загружен! Проверьте CDN или путь к файлу.");
} else {
	console.log("Compromise.js готов к использованию!");
}

// Функция проверки и оборачивания слов
export function processSentence(sentence, selectedWords) {
	let processedSentence = sentence;
	const wordsFound = [];
	const doc = nlp(sentence);

	// Сначала извлечем все слова из скобок в предложении
	const bracketedWords = [];
	const bracketRegex = /\[([^\]]+)\]/g;
	let match;
	while ((match = bracketRegex.exec(sentence)) !== null) {
		bracketedWords.push(match[1].toLowerCase());
	}

	// Обрабатываем все выбранные слова
	selectedWords.forEach((word) => {
		// Нормализуем слово (удаляем скобки если есть и приводим к базовой форме)
		const cleanWord = word.replace(/[\[\]]/g, "").toLowerCase();
		const baseWord = nlp(cleanWord).nouns().toSingular().out("text").toLowerCase() || cleanWord;

		// Проверяем слова в скобках
		bracketedWords.forEach((bracketedWord) => {
			const bracketedBase = nlp(bracketedWord).nouns().toSingular().out("text").toLowerCase() || bracketedWord;
			if (bracketedBase === baseWord) {
				if (!wordsFound.includes(bracketedWord)) {
					wordsFound.push(bracketedWord);
				}
			}
		});

		// Ищем в тексте вне скобок
		const matches = doc.match(word, { caseSensitive: false });
		if (matches.found) {
			matches.terms().forEach((term) => {
				const originalWord = term.text();
				const lowerWord = originalWord.toLowerCase();

				if (!wordsFound.includes(lowerWord)) {
					wordsFound.push(lowerWord);
				}

				if (!originalWord.startsWith("[") || !originalWord.endsWith("]")) {
					processedSentence = processedSentence.replace(new RegExp(`\\b${originalWord}\\b`, "gi"), `[${originalWord}]`);
				}
			});
		}
	});

	return {
		found: wordsFound.length > 0,
		processedSentence: processedSentence,
	};
}
