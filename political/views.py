from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Question, Answer
from django.db.models import Q, F, Value, Case, When, IntegerField
from django.db.models.functions import Lower
from functools import reduce
from operator import or_, and_
import re


def search_question(request):
    return render(request, 'political/search.html')


def normalize_query(query_string):
    """
    Normalizes the query string for better search results:
    1. Preserves the original query for exact matching
    2. Creates individual words for partial matching
    """
    # Store original query (just trimmed spaces and lowercase)
    original_query = query_string.strip().lower()
    
    # Extract individual words for word-based matching
    words = re.findall(r'\w+', original_query)
    
    # Filter out very short words and duplicates
    filtered_words = list(set([word for word in words if len(word) > 1]))
    
    return {
        'original': original_query,
        'words': filtered_words
    }


def ajax_search(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse({'results': []})

    # Get normalized search terms
    search_terms = normalize_query(query)
    original_query = search_terms['original']
    search_words = search_terms['words']
    
    if not search_words and len(original_query) <= 1:
        return JsonResponse({'results': []})

    # First try exact matching - highest priority
    exact_matches = Question.objects.filter(
        Q(question_text__icontains=original_query) | 
        Q(correct_answer__icontains=original_query) |
        Q(answers__answer_text__icontains=original_query)
    ).distinct()

    # Then try word-based matching
    word_conditions = []
    for word in search_words:
        word_conditions.append(Q(question_text__icontains=word))
        word_conditions.append(Q(correct_answer__icontains=word))
        word_conditions.append(Q(answers__answer_text__icontains=word))
    
    # Only apply word conditions if we have valid search words
    if word_conditions:
        word_matches = Question.objects.filter(reduce(or_, word_conditions)).distinct()
        # Combine results, with exact matches first
        results = list(exact_matches) + [q for q in word_matches if q not in exact_matches]
    else:
        results = list(exact_matches)
    
    # Limit results
    results = results[:20]
    
    result_data = []
    for question in results:
        # Get all answers for this question
        answers = Answer.objects.filter(question=question)
        
        # Calculate relevance score
        relevance = 0
        question_text_lower = question.question_text.lower()
        correct_answer_lower = question.correct_answer.lower()
        
        # Exact phrase match has highest priority
        if original_query in question_text_lower:
            relevance += 100  # Very high score for exact question match
        elif original_query in correct_answer_lower:
            relevance += 50   # High score for exact answer match
        
        # Individual word matches add to the score
        for word in search_words:
            if word in question_text_lower:
                relevance += 2  # Word match in question
            if word in correct_answer_lower:
                relevance += 1  # Word match in correct answer
                
            # Check answers for word matches
            for answer in answers:
                if word in answer.answer_text.lower():
                    relevance += 0.5  # Less weight for word in optional answers
        
        result_data.append({
            'question_text': question.question_text,
            'correct_answer': question.correct_answer,
            'answers': [answer.answer_text for answer in answers],
            'relevance': relevance
        })

    # Sort results by relevance score
    result_data.sort(key=lambda x: x['relevance'], reverse=True)
    
    return JsonResponse({'results': result_data})


def add_question(request):
    if request.method == 'POST':
        question_text = request.POST.get('question')
        correct_answer = request.POST.get('correct_answer')
        only_correct = request.POST.get('only_correct')
        new_question = Question.objects.create(question_text=question_text, correct_answer=correct_answer)
        Answer.objects.create(question=new_question, correct_answer=correct_answer)
        if not only_correct:
            answers_raw = request.POST.get('answers', '')
            answers = [a.strip() for a in answers_raw.split(',') if a.strip()]
            for answer_text in answers:
                    Answer.objects.create(question=new_question, answer_text=answer_text)
        # Save AI answers if they exist
        ai_answers = {
            'GPT': request.POST.get('ai_gpt_answer', '').strip(),
            'DeepSeek': request.POST.get('ai_deepseek_answer', '').strip(),
            'Grok': request.POST.get('ai_grok_answer', '').strip(),
            'Copilot': request.POST.get('ai_copilot_answer', '').strip(),
        }
        for ai_name, ai_answer in ai_answers.items():
            if ai_answer:
                Answer.objects.create(question=new_question, answer_text=ai_answer + f' [ИИ: {ai_name}]')
        return redirect('search_question')
    return render(request, 'political/add_questions.html')